import pandas as pd
import os
import keras
from keras.applications import InceptionV3  # ,VGG19
from keras import models
from keras import layers
from keras import optimizers
from keras.preprocessing.image import ImageDataGenerator
import sys
import dill
import numpy as np
from keras.backend import floatx


module_path = os.path.abspath(os.path.join('../label_maker/'))
if module_path not in sys.path:
    sys.path.append(module_path)

import label_maker


def load_model(loc=''):
    """
    Load or instantiate our model.
    :param str loc:  Location of model, if any. Saved as HDF5
    :return models.model model:
    """
    if loc:
        return models.load_model(loc)
        # we must set the fixed part to be fixed
    else:
        conv_base = InceptionV3(weights='imagenet',
                                include_top=False,
                                input_shape=(200, 200, 3))

        model = models.Sequential()
        model.add(conv_base)
        model.add(layers.Flatten())
        model.add(layers.Dense(256, activation='relu'))
        model.add(layers.Dense(51, activation='sigmoid'))
        conv_base.trainable = False


def load_labels(loc):
    """
    Simply loads a dictionary of labels. Useful only if we change this.
    :param loc:
    :return:
    """
    return dill.load(loc)


def build_model(train_path, val_path, model, model_kwargs={}):

    train_generator = train_datagen.flow_from_directory(
        train_path,
        target_size=(200, 200),
        batch_size=20,
        # we have multiple labels for each image
        class_mode='categorical',
        classes=labels_arr.tolist(),
        # interpolation='bilinear'
    )

    validation_generator = val_datagen.flow_from_directory(
        val_path,
        target_size=(200, 200),
        batch_size=20,
        class_mode='categorical',
        classes=labels_arr.tolist(),
        # interpolation='bilinear'
    )

    if not model_kwargs:
        model_kwargs = {
            'loss': 'binary_crossentropy',
            'optimizer': optimizers.RMSprop(lr=2e-5),
            'metrics': ['acc']
        }
    model.compile(**model_kwargs)

    return train_generator, validation_generator


if __name__ == '__main__':
    model = load_model(model_loc)
    label_dict = load_labels(label_loc)

    # This lets our generators use this label_dict as the lookup dictionary
    # without ruining the rest of the algorithm
    ImageDataGenerator.flow_from_directory = label_maker.multilabel_decorator(
        ImageDataGenerator.flow_from_directory, label_dict)

    train_datagen = ImageDataGenerator(
        rescale=1. / 255,
        rotation_range=40.,
        width_shift_range=0.2,
        height_shift_range=0.2,
        shear_range=11.,
        zoom_range=0.2,
        horizontal_flip=True,
        fill_mode='nearest')

    val_datagen = ImageDataGenerator(
        rescale=1. / 255)

    train_dir = tar_dir + "/train"
    validation_dir = tar_dir + "/validation"

    train_generator, validation_generator = build_model(train_dir, validation_dir, model)

    steps_per_epoch = len(label_dict)//train_generator.batch_size  # see approx. all samples

    history = model.fit_generator(
          train_generator,
          steps_per_epoch=steps_per_epoch,
          epochs=20,
          validation_data=validation_generator,
          validation_steps=50
          )

    if save_loc:
        model.save(loc)
        pd.DataFrame(history.history).to_csv(loc+'.history.csv')


