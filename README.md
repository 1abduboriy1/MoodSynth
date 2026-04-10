# MoodSynth

MoodSynth is a local tool that translates plain English text descriptions of moods into real-time synthesized ambient audio. 

It takes a concept like "tense thriller" or "peaceful forest", passes it through a local LLM to map the semantic meaning into physical audio parameters, and generates the matching sound waves from scratch using a pure numpy synthesizer.

## How it works

The signal chain mirrors a DAC (digital-to-analog converter), but at a higher abstraction layer:
1. **Text input:** You type a mood.
2. **Parameter space mapping:** Ollama evaluates the text and returns a strict JSON object containing synthesis parameters (waveform type, base frequency, tremolo depth, reverb depth).
3. **Physical output:** A custom numpy engine builds the sound array frame by frame based on those parameters and pushes it to your speakers via sounddevice.

## Features

- **Local LLM integration:** Uses Ollama so everything runs locally without API keys.
- **Pure Numpy synthesis:** No bulky audio libraries (like pyo) required. It generates sine, square, triangle, sawtooth, and noise waves mathematically.
- **Dynamic effects:** Includes algorithmic reverb and tremolo (amplitude modulation) to give texture to the generated sounds.
- **Auto-normalization:** Built-in volume limiting and envelope fading to prevent audio clipping and hardware pops.

## Setup

1. Install Ollama and pull your preferred model. The script defaults to `llama3`, but you can easily change this in the code.
2. Install the python dependencies:
   ```bash
   pip install numpy sounddevice ollama