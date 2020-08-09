import tensorflow as tf
import numpy as np
import os
from PIL import Image

# read mnist data set
tf.__version__

(train_images, train_labels), (test_images, test_labels) = tf.keras.datasets.mnist.load_data()

train_labels = train_labels[:1000]
test_labels = test_labels[:1000]

train_images = train_images[:1000].reshape(-1, 28 * 28) / 255.0
test_images = test_images[:1000].reshape(-1, 28 * 28) / 255.0

checkpoint_path = "training_1/cp.ckpt"
checkpoint_dir = os.path.dirname(checkpoint_path)
#回调函数
cp_callback = tf.keras.callbacks.ModelCheckpoint(checkpoint_path,
                                                 save_weights_only=True,
                                                 verbose=1)

def create_model():
    model = tf.keras.models.Sequential([
        tf.keras.layers.Flatten(input_shape=(28, 28)),
        tf.keras.layers.Dense(512, activation=tf.nn.relu),
        tf.keras.layers.Dropout(0.2),
        tf.keras.layers.Dense(10, activation=tf.nn.softmax)
    ])
    model.compile(optimizer='adam',
                  loss='sparse_categorical_crossentropy',
                  metrics=['accuracy'])
    return model


def train():
    model = create_model()
    model.fit(train_images, train_labels,  epochs = 10,
          validation_data = (test_images,test_labels),
          callbacks = [cp_callback])  #保存模型
    model.save('my_model1.h5')

def evaluate():
    model = create_model()
    model.load_weights(checkpoint_path)
    model.evaluate(test_images, test_labels)


def predict(path):
    model = create_model()
    model.load_weights(checkpoint_path)
    img = Image.open(path).convert("L")
    img2arr = np.array(img)
    img2arr = (np.expand_dims(img2arr, 0))
    prediction = model.predict(img2arr)
    return int(np.argmax(prediction[0]))
