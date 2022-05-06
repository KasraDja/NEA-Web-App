import numpy as np  # https://towardsdatascience.com/multi-class-text-classification-with-lstm-using-tensorflow-2-0-d88627c10a35
import pandas as pd
from sklearn.utils import class_weight
from sklearn.model_selection import train_test_split
import tensorflow as tf
import tensorflow_hub as hub

CATEGORIES = ['Mathematics', 'Physics', 'Biology', 'Chemistry', 'Medicine', 'Engineering', 'Computer']
weights={}

dataset = pd.read_csv('Scraping_cache.csv')
category_weights = class_weight.compute_class_weight(class_weight='balanced', classes = CATEGORIES, y = dataset['Category'])
#as the dataset i created is unabalanced i have to add weighting to the categories so they are equally proportional
#category_weights is a numpy array
training_set, testing_set = train_test_split(dataset, test_size=0.2, random_state=42)
for index, weight in enumerate(np.sort(category_weights)):
    weights[index] = weight
print(weights)


dataset_train = tf.data.Dataset.from_tensor_slices((training_set['Text'].values, training_set['Category'].values))
dataset_test = tf.data.Dataset.from_tensor_slices((testing_set['Text'].values, testing_set['Category'].values))
table = tf.lookup.StaticHashTable(
    initializer = tf.lookup.KeyValueTensorInitializer(
        keys = tf.constant(CATEGORIES),
        values = tf.constant([0,1,2,3,4,5,6])
    ),
    default_value = tf.constant(-1),
    name="target_encoding"
)
@tf.function
def target(x):
    return table.lookup(x)

def fetch(text, labels):
    return text, tf.one_hot(target(labels),7)

train_data_f=dataset_train.map(fetch)
test_data_f=dataset_test.map(fetch)

hub_layer = hub.KerasLayer("https://tfhub.dev/google/tf2-preview/nnlm-en-dim128/1", output_shape=[128], input_shape=[], 
                            dtype=tf.string, trainable = True)
model = tf.keras.Sequential()
model.add(hub_layer)
model.add(tf.keras.layers.Reshape(target_shape=(128, 1)))
model.add(tf.keras.layers.Bidirectional(tf.keras.layers.LSTM(32, return_sequences=True)))
model.add(tf.keras.layers.Bidirectional(tf.keras.layers.LSTM(16)))
for units in [128, 64]:
  model.add(tf.keras.layers.Dense(units, activation='relu'))
  model.add(tf.keras.layers.Dropout(0.3))
model.add(tf.keras.layers.Dense(7, activation='softmax'))

model.summary()

model.compile(optimizer='adam',
loss=tf.keras.losses.CategoricalCrossentropy(from_logits=True),
metrics =['accuracy'])
train_data_f=train_data_f.shuffle(70000).batch(512)
test_data_f=test_data_f.batch(512)
history = model.fit(train_data_f,epochs=20,validation_data=test_data_f,verbose=1 ,class_weight=weights)
results = model.evaluate(dataset_test.map(fetch).batch(len(list(dataset_test))),verbose=2)
print(results)
model.save('complete_model/')