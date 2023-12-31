# -*- coding: utf-8 -*-
import os
import pandas as pd
import numpy as np
import shutil
from sklearn.model_selection import train_test_split
from sklearn.utils import shuffle
from keras.preprocessing.image import ImageDataGenerator
from keras.layers import Conv2D, MaxPooling2D, Flatten, Dense
from keras.models import Sequential
from keras.optimizers import Adam
from keras.callbacks import EarlyStopping

image_data_url = "https://isic-challenge-data.s3.amazonaws.com/2020/ISIC_2020_Training_JPEG.zip"
metadata_url = "https://isic-challenge-data.s3.amazonaws.com/2020/ISIC_2020_Training_GroundTruth.csv"

data_dir = './data'

if not os.path.exists(os.path.join(data_dir, 'ISIC_2020_Training_JPEG')):
    os.system(f"wget {image_data_url} -P {data_dir}")
    os.system(f"unzip {os.path.join(data_dir, 'ISIC_2020_Training_JPEG.zip')} -d {data_dir}")

metadata = pd.read_csv(metadata_url)

rare_classes = metadata['diagnosis'].value_counts()[metadata['diagnosis'].value_counts() < 100].index
metadata['diagnosis'] = metadata['diagnosis'].apply(lambda x: 'other' if x in rare_classes else x)

metadata['melanoma'] = (metadata['diagnosis'] == 'melanoma').astype(str)

class_counts = metadata['diagnosis'].value_counts()
valid_classes = class_counts[class_counts >= 2].index
metadata_filtered = metadata[metadata['diagnosis'].isin(valid_classes)]
metadata_filtered = shuffle(metadata_filtered, random_state=42)

X_train, X_val, y_train, y_val = train_test_split(
    metadata['image_name'], (metadata['diagnosis'] == 'melanoma').astype(int),  # Use 'diagnosis' for labels
    test_size=0.2, random_state=42, stratify=metadata['diagnosis']
)

train_dir = os.path.join(data_dir, 'train')
val_dir = os.path.join(data_dir, 'validation')

print("X_train (image names):")
print(X_train.head())

print("\ny_train (labels based on 'diagnosis'):")
print(y_train.head())

for class_name in ['melanoma', 'non_melanoma']:
    os.makedirs(os.path.join(train_dir, class_name), exist_ok=True)
    os.makedirs(os.path.join(val_dir, class_name), exist_ok=True)
for image_name, label in zip(X_train, y_train):
    class_name = 'melanoma' if label == 1 else 'non_melanoma'  # Corrected class assignment
    source_path = os.path.join(data_dir, 'train', f'{image_name}.jpg')  # Updated path to 'train' folder
    destination_path = os.path.join(train_dir, class_name, f'{image_name}.jpg')

    # Ensure the source image exists before copying
    if os.path.exists(source_path):
        os.makedirs(os.path.dirname(destination_path), exist_ok=True)
        shutil.copy(source_path, destination_path)
    else:
        print(f"Image not found: {source_path}")

for image_name, label in zip(X_val, y_val):
    class_name = 'melanoma' if label == 1 else 'non_melanoma'
    source_path = os.path.join(data_dir, 'train', f'{image_name}.jpg')  # Updated path to 'train' folder
    destination_path = os.path.join(val_dir, class_name, f'{image_name}.jpg')

    # Ensure the source image exists before copying
    if os.path.exists(source_path):
        os.makedirs(os.path.dirname(destination_path), exist_ok=True)
        shutil.copy(source_path, destination_path)
    else:
        print(f"Image not found: {source_path}")

class_distribution_train = y_train.value_counts()
print("Class distribution in the training set:\n", class_distribution_train)

# Display the class distribution in the validation set
class_distribution_val = y_val.value_counts()
print("\nClass distribution in the validation set:\n", class_distribution_val)

train_dir = os.path.join(data_dir, 'train')
val_dir = os.path.join(data_dir, 'validation')

img_width, img_height = 224, 224
input_shape = (img_width, img_height, 3)
batch_size = 32

# Load and preprocess the training data
train_datagen = ImageDataGenerator(
    rescale=1./255,
    shear_range=0.2,
    zoom_range=0.2,
    horizontal_flip=True)

train_generator = train_datagen.flow_from_directory(
    train_dir,
    target_size=(img_width, img_height),
    batch_size=batch_size,
    class_mode='binary',  # Use 'binary' since we have two classes
    classes=['melanoma', 'non_melanoma']  # Specify the two valid classes
)

# Load and preprocess the validation data
validation_datagen = ImageDataGenerator(rescale=1./255)

validation_generator = validation_datagen.flow_from_directory(
    val_dir,
    target_size=(img_width, img_height),
    batch_size=batch_size,
    class_mode='binary',  # Use 'binary' since we have two classes
    classes=['melanoma', 'non_melanoma']  # Specify the two valid classes
)

def display_directory_structure_summary(directory):
    print("Directory structure summary for", directory)
    for root, dirs, files in os.walk(directory):
        # Exclude hidden directories
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        level = root.replace(directory, '').count(os.sep)
        indent = ' ' * 4 * (level)
        print('{}{}/'.format(indent, os.path.basename(root)), len(files), "files")

# Display the directory structure summary for train_dir
display_directory_structure_summary(train_dir)

def display_directory_structure(directory):
    for root, dirs, files in os.walk(directory):
        level = root.replace(directory, '').count(os.sep)
        indent = ' ' * 4 * (level)
        print('{}{}/'.format(indent, os.path.basename(root)), len(files), "files")

# Display the directory structure for train_dir
display_directory_structure(train_dir)

train_generator_classes = train_generator.class_indices
validation_generator_classes = validation_generator.class_indices

print("Classes in training generator:", train_generator_classes)
print("Classes in validation generator:", validation_generator_classes)
