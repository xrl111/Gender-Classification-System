import 'package:flutter/material.dart';
import 'package:flutter_sound/flutter_sound.dart';
import 'package:permission_handler/permission_handler.dart';
import 'dart:typed_data';
import 'dart:math' as math;

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Gender Classification',
      theme: ThemeData(
        primarySwatch: Colors.green,
        visualDensity: VisualDensity.adaptivePlatformDensity,
      ),
      home: const HomePage(),
    );
  }
}

class HomePage extends StatefulWidget {
  const HomePage({Key? key}) : super(key: key);

  @override
  _HomePageState createState() => _HomePageState();
}

class _HomePageState extends State<HomePage> {
  final FlutterSoundRecorder _recorder = FlutterSoundRecorder();
  bool _isRecording = false;
  String _result = '';
  final int _sampleRate = 16000;
  final int _frameSize = 1024;

  @override
  void initState() {
    super.initState();
    _initRecorder();
  }

  Future<void> _initRecorder() async {
    await _recorder.openRecorder();
    await _recorder.setSubscriptionDuration(const Duration(milliseconds: 10));
  }

  Future<void> _requestPermissions() async {
    await Permission.microphone.request();
  }

  double computeAutocorrelation(List<double> signal) {
    int n = signal.length;
    double maxCorrelation = 0;
    int maxLag = 0;

    for (int k = 50; k < n; k++) {
      double correlation = 0;
      for (int i = 0; i < n - k; i++) {
        correlation += signal[i] * signal[i + k];
      }
      if (correlation > maxCorrelation) {
        maxCorrelation = correlation;
        maxLag = k;
      }
    }

    return _sampleRate / maxLag;
  }

  void _processAudio(Uint8List audioData) {
    // Convert audio data to List<double>
    List<double> samples = [];
    for (int i = 0; i < audioData.length; i += 2) {
      samples.add((audioData[i] | (audioData[i + 1] << 8)) / 32768.0);
    }

    // Normalize samples
    double maxAmplitude = samples.map((x) => x.abs()).reduce(math.max);
    samples = samples.map((x) => x / maxAmplitude).toList();

    // Compute fundamental frequency
    double f0 = computeAutocorrelation(samples);

    // Classify gender
    String gender = f0 >= 165 ? 'Female' : 'Male';

    setState(() {
      _result = 'F0: ${f0.toStringAsFixed(2)} Hz - Gender: $gender';
    });
  }

  Future<void> _startRecording() async {
    await _requestPermissions();
    
    setState(() {
      _isRecording = true;
      _result = 'Recording...';
    });

    await _recorder.startRecorder(
      toStream: true,
      codec: Codec.pcm16,
      numChannels: 1,
      sampleRate: _sampleRate,
    );

    _recorder.onProgress!.listen((e) {
      if (e.decibels != null) {
        _processAudio(e.buffer!);
      }
    });
  }

  Future<void> _stopRecording() async {
    await _recorder.stopRecorder();
    setState(() {
      _isRecording = false;
      _result = 'Recording stopped';
    });
  }

  @override
  void dispose() {
    _recorder.closeRecorder();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Gender Classification'),
      ),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            ElevatedButton(
              onPressed: _isRecording ? null : _startRecording,
              child: const Text('Record'),
            ),
            const SizedBox(height: 20),
            ElevatedButton(
              onPressed: _isRecording ? _stopRecording : null,
              child: const Text('Stop'),
            ),
            const SizedBox(height: 40),
            Text(
              _result,
              style: const TextStyle(fontSize: 20),
              textAlign: TextAlign.center,
            ),
          ],
        ),
      ),
    );
  }
} 