import tensorflow as tf
from . import UnitModule



'''
# String Encoders

'''

def string_encode(string, length):
  MATCH_MAP = [(0x1100, 0x11FF), (0xAC00, 0xD7A4), (0x0000, 0x00FF)] # 11682
  STR_DEPTH2 = 11682
  r = []
  for c in string:
      t = 1
      for s, e in MATCH_MAP:
          if s <= ord(c) and ord(c) <= e:
              t += ord(c) - s
              r.append(t)
              break
          t += e - s
  if len(r) < length:
      r += [0 for _ in range(length - len(r))]
  return r

'''
# UnitModules

'''

class BasicCNNModule(UnitModule):
  def __init__(self,
               char_depth,
               embedding_size,
               filter_size,
               ):
    self.char_depth = char_depth
    self.embedding_size = embedding_size
    self.filter_size = filter_size

  def build(self, unit, input_tensor, dropout_var, optional=True):
    if optional:
      existance = input_tensor.pop(0)
    string_tensor = input_tensor[0]

    with tf.name_scope("BasicCNNModule"):
      emb_table = tf.get_variable('embedding',
                                  shape=(self.char_depth, self.embedding_size),
                                  initializer=tf.glorot_uniform_initializer())
      filter_shape = (self.filter_size, self.embedding_size, 1, unit.vector_size)
      filter_var = tf.get_variable('filter',
                                   shape=filter_shape,
                                   initializer=tf.glorot_normal_initializer())
      bias = tf.get_variable('bias',
                             shape=(unit.vector_size,),
                             initializer=tf.constant_initializer(0.1))

      # Convolution Layer
      embd_input = tf.nn.embedding_lookup(emb_table, string_tensor)
      embd_input = tf.expand_dims(embd_input, -1)

      # Convolution Layer
      conv = tf.nn.conv2d(embd_input,
                          filter_var,
                          strides=[1, 1, 1, 1],
                          padding='VALID',
                          name='conv')
      # Apply nonlinearity
      biased= tf.nn.relu(tf.nn.bias_add(conv, bias), name='relu')
      # Max-pooling over the outputs
      string_length = unit.string_length
      pooled = tf.nn.max_pool(biased,
                              ksize=[1, string_length - self.filter_size + 1, 1, 1],
                              strides=[1, 1, 1, 1],
                              padding='VALID',
                              name='pool')
      pooled = tf.nn.dropout(pooled, dropout_var)
      result_vector = tf.squeeze(pooled, [1, 2])
      if optional:
        pass # TODO: combine existance to outputs
      return result_vector
