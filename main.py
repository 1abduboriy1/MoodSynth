import json
import re
import numpy as np
import sounddevice as sd
import ollama

def get_synth_params(mood):
    prompt = f"""
    Map this mood to audio synth parameters. 
    Return ONLY valid JSON. No markdown formatting, no explanations, no text outside the braces.
    
    Required keys:
    - "base_frequency" (float, 50.0 to 800.0)
    - "waveform" (string: "sine", "square", "triangle", "sawtooth", or "noise")
    - "reverb_depth" (float, 0.0 to 1.0)
    - "tremolo_depth" (float, 0.0 to 1.0)
    - "duration" (int, 3 to 8)

    Mood: "{mood}"
    """
    
    # using llama3, swap this out if you're running mistral or something else locally
    res = ollama.chat(model='llama3', messages=[{'role': 'user', 'content': prompt}])
    raw = res['message']['content'].strip()
    
    # clean up markdown backticks if the llm ignores instructions
    raw = re.sub(r'^```json', '', raw, flags=re.MULTILINE)
    raw = re.sub(r'^```', '', raw, flags=re.MULTILINE)
    
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        print("json parse failed. falling back to default params.")
        return {
            "base_frequency": 200.0,
            "waveform": "sine",
            "reverb_depth": 0.5,
            "tremolo_depth": 0.1,
            "duration": 4
        }

def generate_sound(params):
    sr = 44100
    dur = params.get('duration', 4)
    t = np.linspace(0, dur, int(sr * dur), False)
    
    freq = params.get('base_frequency', 200.0)
    wave = params.get('waveform', 'sine')
    
    # base waveform generation
    if wave == 'sine':
        audio = np.sin(2 * np.pi * freq * t)
    elif wave == 'square':
        audio = np.sign(np.sin(2 * np.pi * freq * t))
    elif wave == 'triangle':
        audio = 2 * np.abs(2 * (t * freq - np.floor(t * freq + 0.5))) - 1
    elif wave == 'sawtooth':
        audio = 2 * (t * freq - np.floor(t * freq + 0.5))
    elif wave == 'noise':
        audio = np.random.uniform(-1, 1, len(t))
    else:
        audio = np.sin(2 * np.pi * freq * t)

    # new effect: tremolo (amplitude modulation at 4hz)
    trem_depth = params.get('tremolo_depth', 0.0)
    if trem_depth > 0:
        mod = 1.0 - trem_depth + trem_depth * np.sin(2 * np.pi * 4.0 * t) 
        audio *= mod

    # basic delay-based reverb
    rev_depth = params.get('reverb_depth', 0.0)
    if rev_depth > 0:
        delay = int(sr * 0.15)
        delayed = np.zeros_like(audio)
        delayed[delay:] = audio[:-delay]
        audio += delayed * rev_depth

    # quick fade in/out to prevent clicks at the start and end
    fade = int(sr * 0.05)
    env = np.ones_like(audio)
    env[:fade] = np.linspace(0, 1, fade)
    env[-fade:] = np.linspace(1, 0, fade)
    audio *= env

    # normalize and drop volume to avoid harsh clipping on the speakers
    if np.max(np.abs(audio)) > 0:
        audio = audio / np.max(np.abs(audio)) * 0.25
        
    return audio, sr

def main():
    print("MoodSynth loaded.")
    print("Type a mood description (e.g. 'calm rainy night', 'tense thriller') or 'q' to quit.")
    
    while True:
        mood = input("\nMood: ")
        if mood.lower() in ['q', 'quit', 'exit']:
            break
            
        print("Translating...")
        params = get_synth_params(mood)
        print(f"Generated params: {params}")
        
        print("Playing audio...")
        audio, sr = generate_sound(params)
        
        sd.play(audio, sr)
        sd.wait()

if __name__ == '__main__':
    main()