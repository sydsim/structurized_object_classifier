

class ConcatFCNModel(UnitModel):
  def struct(self, unit, input_tensor, dropout_var):
    with tf.name_scope("ListStruct"):
      cells = [unit.elem]
      for i in range(2):
          cell = tf.contrib.rnn.LSTMCell(num_units=unit.vector_size)
          if i == 0:
              # Add attention wrapper to first layer.
              cell = tf.contrib.rnn.AttentionCellWrapper(cell, 32, state_is_tuple=True)
          cell = tf.contrib.rnn.DropoutWrapper(cell, output_keep_prob=dropout_var)
          cells.append(cell)

      sequence_length = input_tensor[-1]
      data_tensor = input_tensor[:-1]

      elem_cell = tf.contrib.rnn.MultiRNNCell(cells)
      self.elem.dropout_var = dropout_var
      output, state = tf.nn.dynamic_rnn(elem_cell,
                                        data_tensor,
                                        sequence_length=sequence_length,
                                        dtype=tf.float32)

      batch_range = tf.range(tf.shape(output)[0])
      indices = tf.stack([batch_range, sequence_length-1], axis=1)
      res = tf.gather_nd(output, indices)
      self.test = []
      return res
