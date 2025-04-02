from flask import Flask, request, jsonify, render_template
import numpy as np
import json

app = Flask(__name__)

def compute_autocorrelation(signal):
    """Compute autocorrelation of the signal."""
    n = len(signal)
    autocorr = np.zeros(n)
    
    for k in range(n):
        autocorr[k] = np.sum(signal[:n-k] * signal[k:])
    
    return autocorr

def find_fundamental_frequency(signal, sample_rate=16000):
    """Find fundamental frequency using autocorrelation."""
    # Normalize signal
    signal = signal / (np.max(np.abs(signal)) + 1e-10)  # Avoid division by zero
    
    # Compute autocorrelation
    autocorr = compute_autocorrelation(signal)
    
    # Find first significant peak after k=50
    # This helps avoid detecting harmonics
    peak_idx = np.argmax(autocorr[50:]) + 50
    
    # Calculate fundamental frequency
    f0 = sample_rate / peak_idx if peak_idx > 0 else 0
    
    return f0

def is_valid_voice(frame, threshold=0.001):
    """Check if the frame contains valid voice data."""
    # Calculate energy
    energy = np.mean(frame ** 2)
    
    # Calculate zero-crossing rate
    zero_crossings = np.sum(np.abs(np.diff(np.signbit(frame)))) / (2 * len(frame))
    
    # Check periodicity using autocorrelation
    autocorr = compute_autocorrelation(frame)
    periodicity = np.max(autocorr[50:]) / (autocorr[0] + 1e-10)
    
    # Conditions for valid voice:
    # 1. Sufficient energy
    # 2. Reasonable zero-crossing rate
    # 3. Good periodicity
    return (energy > threshold and 
            zero_crossings < 0.4 and
            periodicity > 0.2)

def process_audio_frames(audio_data, frame_size=1024, sample_rate=16000):
    """Process audio data in frames and return F0 values over time."""
    audio_data = np.array(audio_data)
    
    # Normalize audio data
    audio_data = audio_data / (np.max(np.abs(audio_data)) + 1e-10)
    
    n_frames = len(audio_data) // frame_size
    f0_values = []
    timestamps = []
    valid_frames = 0
    total_frames = 0
    
    # Add padding to avoid losing information at the edges
    padded_audio = np.pad(audio_data, (frame_size//2, frame_size//2), mode='reflect')
    
    for i in range(n_frames):
        start_idx = i * frame_size
        end_idx = start_idx + frame_size
        # Use Hanning window to reduce edge noise
        window = np.hanning(frame_size)
        frame = padded_audio[start_idx:end_idx] * window
        total_frames += 1
        
        # Check if frame contains valid voice
        if is_valid_voice(frame):
            valid_frames += 1
            f0 = find_fundamental_frequency(frame, sample_rate)
            if 40 <= f0 <= 500:  # Expand frequency range
                f0_values.append(f0)
                timestamps.append(start_idx)
    
    # Calculate voice ratio
    voice_ratio = valid_frames / total_frames if total_frames > 0 else 0
    
    return f0_values, timestamps, voice_ratio

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/classify', methods=['POST'])
def classify_gender():
    try:
        # Get audio data from request
        data = request.get_json()
        audio_data = np.array(data['audio_data'])
        
        # Check if audio data is empty or too short
        if len(audio_data) < 1024:
            return jsonify({
                'error': 'Audio recording is too short. Please record a longer sample.'
            }), 400
        
        # Process audio in frames
        f0_values, timestamps, voice_ratio = process_audio_frames(audio_data)
        
        # Reduce voice ratio requirement
        if voice_ratio < 0.05:  # Reduce from 0.1 to 0.05 (5% frames with voice)
            return jsonify({
                'error': 'No clear voice detected. Please speak clearly and try again.',
                'details': {
                    'voice_ratio': voice_ratio,
                    'message': 'The recording contains mostly silence or noise. Try speaking louder or closer to the microphone.'
                }
            }), 400
        
        if not f0_values:
            return jsonify({
                'error': 'Could not analyze voice characteristics. Please try again.',
                'details': {
                    'voice_ratio': voice_ratio,
                    'message': 'Try speaking more clearly and sustained vowel sounds.'
                }
            }), 400
        
        # Calculate average F0 (use median instead of mean to reduce noise)
        average_f0 = np.median(f0_values)
        
        # Classify gender based on average F0
        gender = "Female" if average_f0 >= 165 else "Male"
        
        # Add confidence level based on voice ratio and F0 consistency
        f0_std = np.std(f0_values)
        f0_consistency = 1 - min(f0_std / average_f0, 1)  # Higher consistency = lower std dev
        # Adjust confidence formula
        confidence = (voice_ratio * 0.7 + f0_consistency * 0.3) * 100  # Increase weight for voice_ratio
        
        return jsonify({
            'average_f0': float(average_f0),
            'gender': gender,
            'f0_values': [float(f0) for f0 in f0_values],
            'timestamps': timestamps,
            'analysis_details': {
                'confidence': round(confidence, 1),
                'voice_ratio': round(voice_ratio * 100, 1),
                'f0_consistency': round(f0_consistency * 100, 1)
            }
        })
        
    except Exception as e:
        return jsonify({
            'error': 'An error occurred during analysis.',
            'details': str(e)
        }), 400

if __name__ == '__main__':
    app.run(debug=True) 