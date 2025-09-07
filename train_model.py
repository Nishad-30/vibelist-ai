"""
Training script for the Thematic Playlist Generator AI model
"""

import json
import pickle
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
from sklearn.preprocessing import LabelEncoder
import config

def load_training_data():
    """Load and preprocess training data"""
    with open(config.TRAINING_DATA_PATH, 'r') as f:
        data = json.load(f)
    
    # Extract features and labels
    vibes = []
    genre_lists = []
    energy_levels = []
    valence_levels = []
    characteristics = []
    
    for item in data:
        vibes.append(item['vibe'])
        # Take the first genre as primary genre for classification
        primary_genre = item['genres'][0] if item['genres'] else 'unknown'
        genre_lists.append(primary_genre)
        energy_levels.append(item['energy'])
        valence_levels.append(item['valence'])
        characteristics.append(' '.join(item['characteristics']))
    
    return vibes, genre_lists, energy_levels, valence_levels, characteristics

def create_features(vibes, characteristics):
    """Create feature vectors from text data"""
    # Combine vibe descriptions with characteristics
    combined_text = [f"{vibe} {char}" for vibe, char in zip(vibes, characteristics)]
    
    # Create TF-IDF vectorizer
    vectorizer = TfidfVectorizer(
        max_features=100,  # Very small for tiny dataset
        ngram_range=(1, 1),  # Only unigrams for small dataset
        stop_words='english',
        lowercase=True,
        min_df=1  # Important for small datasets
    )
    
    # Fit and transform the text data
    features = vectorizer.fit_transform(combined_text)
    
    return features, vectorizer

def train_genre_classifier(features, genres):
    """Train a classifier to predict music genres"""
    # Encode genre labels
    label_encoder = LabelEncoder()
    encoded_genres = label_encoder.fit_transform(genres)
    
    print(f"Number of unique genres: {len(label_encoder.classes_)}")
    print(f"Genres: {list(label_encoder.classes_)}")
    
    # For very small datasets, use simple random split without stratification
    # Use larger test size to ensure we have some test data
    if len(genres) <= 15:  # Small dataset
        X_train, X_test, y_train, y_test = train_test_split(
            features, encoded_genres, test_size=0.4, random_state=42, shuffle=True
        )
    else:
        X_train, X_test, y_train, y_test = train_test_split(
            features, encoded_genres, test_size=0.2, random_state=42
        )
    
    # Use shape[0] for sparse matrices
    print(f"Training samples: {X_train.shape[0]}, Test samples: {X_test.shape[0]}")
    
    # Train Random Forest classifier with minimal settings for small datasets
    classifier = RandomForestClassifier(
        n_estimators=10,  # Very small for tiny dataset
        random_state=42,
        max_depth=3,  # Shallow to prevent overfitting
        min_samples_split=2,
        min_samples_leaf=1
    )
    classifier.fit(X_train, y_train)
    
    # Evaluate model only if we have test samples
    if X_test.shape[0] > 0:
        y_pred = classifier.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        print(f"Genre Classification Accuracy: {accuracy:.3f}")
        
        try:
            print("\nClassification Report:")
            unique_labels = np.unique(np.concatenate([y_test, y_pred]))
            target_names = [label_encoder.classes_[i] for i in unique_labels]
            print(classification_report(y_test, y_pred, labels=unique_labels, target_names=target_names, zero_division=0))
        except Exception as e:
            print(f"Could not generate detailed classification report: {e}")
    else:
        print("No test samples available - using full dataset for training")
    
    return classifier, label_encoder

def train_energy_valence_regressors(features, energy_levels, valence_levels):
    """Train regressors for energy and valence prediction"""
    from sklearn.ensemble import RandomForestRegressor
    from sklearn.metrics import mean_squared_error, r2_score
    
    # For small datasets, use simple split
    if len(energy_levels) <= 15:
        test_size = 0.4
    else:
        test_size = 0.2
    
    # Split data
    X_train, X_test, y_energy_train, y_energy_test = train_test_split(
        features, energy_levels, test_size=test_size, random_state=42
    )
    _, _, y_valence_train, y_valence_test = train_test_split(
        features, valence_levels, test_size=test_size, random_state=42
    )
    
    print(f"Regression training samples: {X_train.shape[0]}, test samples: {X_test.shape[0]}")
    
    # Train energy regressor
    energy_regressor = RandomForestRegressor(
        n_estimators=10, 
        random_state=42,
        max_depth=3
    )
    energy_regressor.fit(X_train, y_energy_train)
    
    # Train valence regressor
    valence_regressor = RandomForestRegressor(
        n_estimators=10, 
        random_state=42,
        max_depth=3
    )
    valence_regressor.fit(X_train, y_valence_train)
    
    # Evaluate models
    if X_test.shape[0] > 0:
        energy_pred = energy_regressor.predict(X_test)
        valence_pred = valence_regressor.predict(X_test)
        
        try:
            energy_r2 = r2_score(y_energy_test, energy_pred)
            valence_r2 = r2_score(y_valence_test, valence_pred)
            
            print(f"\nEnergy Prediction R²: {energy_r2:.3f}")
            print(f"Energy RMSE: {np.sqrt(mean_squared_error(y_energy_test, energy_pred)):.3f}")
            
            print(f"Valence Prediction R²: {valence_r2:.3f}")
            print(f"Valence RMSE: {np.sqrt(mean_squared_error(y_valence_test, valence_pred)):.3f}")
        except Exception as e:
            print(f"Could not compute R² scores: {e}")
    else:
        print("No test samples for regression evaluation")
    
    return energy_regressor, valence_regressor

def save_models(vectorizer, genre_classifier, genre_encoder, energy_regressor, valence_regressor):
    """Save all trained models"""
    model_data = {
        'vectorizer': vectorizer,
        'genre_classifier': genre_classifier,
        'genre_encoder': genre_encoder,
        'energy_regressor': energy_regressor,
        'valence_regressor': valence_regressor
    }
    
    with open(config.MODEL_PATH, 'wb') as f:
        pickle.dump(model_data, f)
    
    print(f"\nModels saved to {config.MODEL_PATH}")

def main():
    """Main training pipeline"""
    print("Loading training data...")
    vibes, genres, energy_levels, valence_levels, characteristics = load_training_data()
    
    print(f"Loaded {len(vibes)} training examples")
    print(f"Unique genres: {set(genres)}")
    
    print("Creating features...")
    features, vectorizer = create_features(vibes, characteristics)
    print(f"Feature matrix shape: {features.shape}")
    
    print("Training genre classifier...")
    genre_classifier, genre_encoder = train_genre_classifier(features, genres)
    
    print("Training energy and valence regressors...")
    energy_regressor, valence_regressor = train_energy_valence_regressors(
        features, energy_levels, valence_levels
    )
    
    print("Saving models...")
    save_models(vectorizer, genre_classifier, genre_encoder, energy_regressor, valence_regressor)
    
    print("\n✅ Training completed successfully!")
    print("You can now run the Streamlit app with: streamlit run app.py")
    
    # Test the model with a sample input
    print("\n🧪 Testing model with sample inputs...")
    test_vibes = [
        "chill evening music",
        "energetic workout session", 
        "romantic dinner atmosphere"
    ]
    
    for test_vibe in test_vibes:
        test_features = vectorizer.transform([test_vibe])
        
        predicted_genre_idx = genre_classifier.predict(test_features)[0]
        predicted_genre = genre_encoder.inverse_transform([predicted_genre_idx])[0]
        predicted_energy = energy_regressor.predict(test_features)[0]
        predicted_valence = valence_regressor.predict(test_features)[0]
        
        print(f"\nTest: '{test_vibe}'")
        print(f"  → Genre: {predicted_genre}")
        print(f"  → Energy: {predicted_energy:.3f}")
        print(f"  → Valence: {predicted_valence:.3f}")

if __name__ == "__main__":
    main()