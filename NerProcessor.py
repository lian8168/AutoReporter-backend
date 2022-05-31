from bert4keras.tokenizers import Tokenizer
from bert4keras.snippets import ViterbiDecoder, to_array
from bert4keras.models import build_transformer_model
from bert4keras.optimizers import Adam
from bert4keras.layers import ConditionalRandomField
from bert4keras.backend import K, keras, search_layer
import numpy as np
import pickle




def adversarial_training(model, embedding_name, epsilon=1):
    """给模型添加对抗训练
            其中model是需要添加对抗训练的keras模型，embedding_name
            则是model里边Embedding层的名字。要在模型compile之后使用。
            """
    if model.train_function is None:  # 如果还没有训练函数
        model._make_train_function()  # 手动make
    old_train_function = model.train_function  # 备份旧的训练函数

    # 查找Embedding层
    for output in model.outputs:
        embedding_layer = search_layer(output, embedding_name)
        if embedding_layer is not None:
            break
    if embedding_layer is None:
        raise Exception('Embedding layer not found')

    # 求Embedding梯度
    embeddings = embedding_layer.embeddings  # Embedding矩阵
    gradients = K.gradients(model.total_loss, [embeddings])  # Embedding梯度
    gradients = K.zeros_like(embeddings) + gradients[0]  # 转为dense tensor

    # 封装为函数
    inputs = (model._feed_inputs +
              model._feed_targets +
              model._feed_sample_weights)  # 所有输入层
    embedding_gradients = K.function(
        inputs=inputs,
        outputs=[gradients],
        name='embedding_gradients',
    )  # 封装为函数

    def train_function(inputs):  # 重新定义训练函数
        grads = embedding_gradients(inputs)[0]  # Embedding梯度
        delta = epsilon * grads / (np.sqrt((grads ** 2).sum()) + 1e-8)  # 计算扰动
        K.set_value(embeddings, K.eval(embeddings) + delta)  # 注入扰动
        outputs = old_train_function(inputs)  # 梯度下降
        K.set_value(embeddings, K.eval(embeddings) - delta)  # 删除扰动
        return outputs

    model.train_function = train_function  # 覆盖原训练函数


class SetLearningRate:
    """层的一个包装，用来设置当前层的学习率
    """

    def __init__(self, layer, lamb, is_ada=False):
        self.layer = layer
        self.lamb = lamb  # 学习率比例
        self.is_ada = is_ada  # 是否自适应学习率优化器

    def __call__(self, inputs):
        with K.name_scope(self.layer.name):
            if not self.layer.built:
                input_shape = K.int_shape(inputs)
                self.layer.build(input_shape)
                self.layer.built = True
                if self.layer._initial_weights is not None:
                    self.layer.set_weights(self.layer._initial_weights)
        for key in ['kernel', 'bias', 'embeddings', 'depthwise_kernel', 'pointwise_kernel', 'recurrent_kernel', 'gamma',
                    'beta']:
            if hasattr(self.layer, key):
                weight = getattr(self.layer, key)
                if self.is_ada:
                    lamb = self.lamb  # 自适应学习率优化器直接保持lamb比例
                else:
                    lamb = self.lamb ** 0.5  # SGD（包括动量加速），lamb要开平方
                K.set_value(weight, K.eval(weight) / lamb)  # 更改初始化
                setattr(self.layer, key, weight * lamb)  # 按比例替换
        return self.layer(inputs)


class NamedEntityRecognizer(ViterbiDecoder):
    """命名实体识别器
    """

    def recognize(self, model, id2label, max_len, tokenizer, text):
        tokens = tokenizer.tokenize(text)
        while len(tokens) > max_len:
            tokens.pop(-2)
        mapping = tokenizer.rematch(text, tokens)
        token_ids = tokenizer.tokens_to_ids(tokens)
        segment_ids = [0] * len(token_ids)
        token_ids, segment_ids = to_array([token_ids], [segment_ids])  # ndarray
        nodes = model.predict([token_ids, segment_ids])[0]  # [sqe_len,23]
        labels = self.decode(nodes)  # id [sqe_len,], [0 0 0 0 0 7 8 8 0 0 0 0 0 0 0]
        entities, starting = [], False
        for i, label in enumerate(labels):
            if label > 0:
                if label % 2 == 1:
                    starting = True
                    entities.append([[i], id2label[(label - 1) // 2]])
                elif starting:
                    entities[-1][0].append(i)
                else:
                    starting = False
            else:
                starting = False
        return [(text[mapping[w[0]][0]:mapping[w[-1]][-1] + 1], l) for w, l in entities]


class Ner:
    def __init__(self, checkpoint_save_path, entity_labels, max_len, lstm_units, drop_rate, leraning_rate, epsilon, lamb):
        # self.epochs = 4
        # self.batch_size = 16
        self.max_len = max_len
        self.lstm_units = lstm_units
        self.drop_rate = drop_rate
        self.leraning_rate = leraning_rate
        self.epsilon = epsilon
        self.lamb = lamb
        self.config_path = 'D:/finalTask/bert_bilstm_crf_keras_self/pre_model/chinese_bert_wwm/bert_config.json'
        self.checkpoint_path = 'D:/finalTask/bert_bilstm_crf_keras_self/pre_model/chinese_bert_wwm/bert_model.ckpt'
        vocab_path = 'D:/finalTask/bert_bilstm_crf_keras_self/pre_model/chinese_bert_wwm/vocab.txt'
        self.tokenizer = Tokenizer(vocab_path, do_lower_case=True)
        self.checkpoint_save_path = checkpoint_save_path
        self.entity_labels = entity_labels
        self.id2label = {i: j for i, j in enumerate(sorted(self.entity_labels))}
        self.label2id = {j: i for i, j in self.id2label.items()}
        self.num_labels = len(self.entity_labels) * 2 + 1  # b i o
        self.model, self.CRF = self.bert_bilstm_crf(self.config_path, self.checkpoint_path, self.num_labels,
                                                    self.lstm_units, self.drop_rate, self.leraning_rate, self.lamb)
        adversarial_training(self.model, 'Embedding-Token', self.epsilon)
        self.NER = NamedEntityRecognizer(trans=K.eval(self.CRF.trans), starts=[0], ends=[0])

    def bert_bilstm_crf(self, config_path, checkpoint_path, num_labels, lstm_units, drop_rate, leraning_rate, lamb):
        bert = build_transformer_model(
            config_path=config_path,
            checkpoint_path=checkpoint_path,
            model='bert',
            return_keras_model=False
        )
        x = bert.model.output  # [batch_size, seq_length, 768]
        lstm = SetLearningRate(
            keras.layers.Bidirectional(
                keras.layers.LSTM(
                    lstm_units,
                    kernel_initializer='he_normal',
                    return_sequences=True
                )
            ),
            lamb,
            True
        )(x)  # [batch_size, seq_length, lstm_units * 2]

        x = keras.layers.concatenate(
            [lstm, x],
            axis=-1
        )  # [batch_size, seq_length, lstm_units * 2 + 768]

        x = keras.layers.TimeDistributed(
            keras.layers.Dropout(drop_rate)
        )(x)  # [batch_size, seq_length, lstm_units * 2 + 768]

        x = SetLearningRate(
            keras.layers.TimeDistributed(
                keras.layers.Dense(
                    num_labels,
                    activation='relu',
                    kernel_initializer='he_normal',
                )
            ),
            lamb,
            True
        )(x)  # [batch_size, seq_length, num_labels]

        crf = ConditionalRandomField()
        output = crf(x)

        model = keras.models.Model(bert.input, output)
        model.summary()
        model.compile(
            loss=crf.sparse_loss,
            optimizer=Adam(leraning_rate),
            metrics=[crf.sparse_accuracy]
        )

        return model, crf

    def perdict(self, text):
        self.model.load_weights(self.checkpoint_save_path + '/bert_bilstm_crf.weights')
        # model = keras.models.load_model(checkpoint_save_path,
        #                                 compile=False)
        self.NER.trans = pickle.load(open(self.checkpoint_save_path + '/crf_trans.pkl', 'rb'))
        return self.NER.recognize(self.model, self.id2label, self.max_len, self.tokenizer, text)
