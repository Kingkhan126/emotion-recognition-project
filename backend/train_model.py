import os
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.callbacks import ModelCheckpoint, EarlyStopping, ReduceLROnPlateau
from create_placeholder_model import create_model

def train_emotion_model():
    batch_size = 64
    num_epochs = 50

    base_dir = os.path.dirname(__file__)
    train_dir = os.path.join(base_dir, 'dataset', 'train')
    val_dir = os.path.join(base_dir, 'dataset', 'test')

    if not os.path.exists(train_dir) or not os.path.exists(val_dir):
        print("ERROR: FER-2013 dataset not found in 'dataset/train' and 'dataset/test'.")
        return

    print("Loading data with augmentation...")
    
    # Data Augmentation for training
    train_datagen = ImageDataGenerator(
        rescale=1./255,
        rotation_range=15,
        width_shift_range=0.15,
        height_shift_range=0.15,
        shear_range=0.15,
        zoom_range=0.15,
        horizontal_flip=True,
    )

    # Only rescale for validation
    val_datagen = ImageDataGenerator(rescale=1./255)

    # Note: flow_from_directory automatically sorts classes alphabetically:
    # Angry, Disgust, Fear, Happy, Neutral, Sad, Surprise
    train_generator = train_datagen.flow_from_directory(
        train_dir,
        target_size=(48, 48),
        batch_size=batch_size,
        color_mode="grayscale",
        class_mode='categorical',
        shuffle=True
    )

    validation_generator = val_datagen.flow_from_directory(
        val_dir,
        target_size=(48, 48),
        batch_size=batch_size,
        color_mode="grayscale",
        class_mode='categorical',
        shuffle=False
    )

    # Load architecture
    print("Initializing CNN Architecture...")
    model = create_model()

    model_dir = os.path.join(base_dir, 'model')
    if not os.path.exists(model_dir):
        os.makedirs(model_dir)
        
    model_path = os.path.join(model_dir, 'emotion_model.hdf5')

    # Callbacks to prevent overfitting
    checkpoint = ModelCheckpoint(model_path, monitor='val_accuracy', verbose=1, save_best_only=True, mode='max')
    early_stopping = EarlyStopping(monitor='val_loss', patience=10, verbose=1, restore_best_weights=True)
    reduce_lr = ReduceLROnPlateau(monitor='val_loss', factor=0.2, patience=3, verbose=1, min_lr=0.00001)

    callbacks_list = [checkpoint, early_stopping, reduce_lr]

    print("Starting training...")
    history = model.fit(
        train_generator,
        steps_per_epoch=train_generator.n // train_generator.batch_size,
        epochs=num_epochs,
        validation_data=validation_generator,
        validation_steps=validation_generator.n // validation_generator.batch_size,
        callbacks=callbacks_list
    )

    print("Training finished! Best model saved to:", model_path)

if __name__ == '__main__':
    train_emotion_model()
