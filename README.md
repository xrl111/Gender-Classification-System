# Gender Classification System

A real-time gender classification system based on voice analysis using fundamental frequency (F0) detection.

## System Overview

The system consists of two applications:

1. Web Application (Flask + Web Audio API)
2. Mobile Application (Flutter for Android)

Both applications use the same core algorithm:

- Sample rate: 16 kHz
- Frame size: 1024 samples
- Feature: Fundamental frequency (F0) via autocorrelation
- Classification threshold: 165 Hz (F0 < 165 Hz → Male, F0 ≥ 165 Hz → Female)

## Web Application Setup

### Prerequisites

- Python 3.7+
- pip

### Installation

1. Create a virtual environment (optional but recommended):

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

### Running the Web Application

1. Start the Flask server:

```bash
python app.py
```

2. Open your web browser and navigate to:

```
http://localhost:5000
```

## Mobile Application Setup

### Prerequisites

- Flutter SDK
- Android Studio
- Android device or emulator

### Installation

1. Install Flutter dependencies:

```bash
flutter pub get
```

2. Run the application:

```bash
flutter run
```

## Usage

### Web Application

1. Click the "Record" button to start recording
2. Speak into your microphone
3. The system will display the detected F0 and gender classification
4. Click "Stop" to end recording

### Mobile Application

1. Launch the app
2. Grant microphone permissions when prompted
3. Tap the "Record" button to start recording
4. Speak into your device's microphone
5. The system will display the detected F0 and gender classification
6. Tap "Stop" to end recording

## Notes

- The system works best with clear, sustained vowel sounds
- Background noise may affect accuracy
- Results are displayed in real-time
- The classification is based on a simple threshold and may not be accurate for all voices

## License

MIT License
