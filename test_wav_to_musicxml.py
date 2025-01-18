"""
test_wav_to_musicxml.py

1) librosa를 통해 test.wav에서 음높이 추출
2) pretty_midi를 통해 추출된 음높이를 MIDI로 변환
3) music21을 통해 MIDI를 MusicXML로 변환
"""

import os
import librosa
import numpy as np
import pretty_midi
from music21 import converter
from librosa import hz_to_midi

def wav_to_midi(input_wav: str, output_mid: str):
    print(f"[INFO] Loading WAV file: {input_wav}")
    y, sr = librosa.load(input_wav, sr=None)

    print("[INFO] Extracting pitches using librosa.piptrack...")
    pitches, magnitudes = librosa.piptrack(y=y, sr=sr)

    print("[INFO] Processing pitches...")
    notes = []
    for t in range(pitches.shape[1]):
        index = magnitudes[:, t].argmax()
        pitch = pitches[index, t]
        if pitch > 0:
            # 주파수를 MIDI 노트 번호로 변환
            midi_pitch = int(round(hz_to_midi(pitch)))
            # MIDI 노트 번호 범위(0-127)로 클램핑
            midi_pitch = max(0, min(127, midi_pitch))
            notes.append(midi_pitch)

    if not notes:
        print("[ERROR] No notes detected in the audio.")
        return False

    print("[INFO] Creating MIDI file...")
    midi = pretty_midi.PrettyMIDI()
    piano = pretty_midi.Instrument(program=pretty_midi.instrument_name_to_program('Acoustic Grand Piano'))

    start_time = 0
    duration = 0.5  # 각 노트의 지속시간 (초)
    for pitch in notes:
        note = pretty_midi.Note(velocity=100, pitch=pitch, start=start_time, end=start_time + duration)
        piano.notes.append(note)
        start_time += duration

    midi.instruments.append(piano)
    midi.write(output_mid)
    print(f"[INFO] MIDI 파일 생성 완료: {output_mid}")
    return True

def midi_to_musicxml(input_mid: str, output_xml: str):
    print(f"[INFO] Converting MIDI to MusicXML...\n Input: {input_mid}\n Output: {output_xml}")
    try:
        # MIDI 로드
        score = converter.parse(input_mid)

        # 필요한 경우 키 분석 (선택적)
        key_analysis = score.analyze('KrumhanslSchmuckler')
        print(f"추정 키: {key_analysis}")

        # MusicXML로 내보내기
        score.write('musicxml', fp=output_xml)
        print("[INFO] MusicXML 악보 생성 완료.")
        return True
    except Exception as e:
        print(f"[ERROR] MIDI to MusicXML 변환 중 오류 발생: {e}")
        return False

def main():
    # 사용자가 준비한 WAV 파일 이름
    input_wav = "test.wav"

    # 변환할 MIDI 및 MusicXML 파일 이름
    output_mid = "converted.mid"
    output_xml = "converted_musicxml.xml"

    # WAV → MIDI 변환
    success = wav_to_midi(input_wav, output_mid)
    if not success:
        print("[ERROR] WAV → MIDI 변환 실패. 프로그램을 종료합니다.")
        return

    # MIDI → MusicXML 변환
    success = midi_to_musicxml(output_mid, output_xml)
    if not success:
        print("[ERROR] MIDI → MusicXML 변환 실패.")
        return

    # 변환 후 결과 메시지
    if os.path.exists(output_xml):
        print("[DONE] 최종 MusicXML 파일 생성:", output_xml)
    else:
        print("[ERROR] MusicXML 파일 생성 실패.")

if __name__ == "__main__":
    main()
