import streamlit as st
import random
import base64
import re

# 캐릭터와 성별 정의
characters = {
    "Paul": "male", "Jello": "male", "Uju": "male", "Khan": "male", "Eric": "male",
    "Bora": "female", "Tina": "female", "Amy": "female"
}

def generate_question():
    questions = [
        "Look at the {animal}.",
    ]
    
    animals = {
        "bird 🐤": "It's small.",
        "lion 🦁": "It's big.",
        "tiger 🐅": "It's big.",
        "elephant 🐘": "It's big.",
        "zebra 🦓": "It's cute.",
        "giraffe 🦒": "It's tall."
    }
    
    korean_question = "동물의 모습은 어떠한가요?"
    korean_options = ["작다", "크다", "귀엽다", "키가 크다"]
    
    selected_question = random.choice(questions)
    selected_animal, selected_answer = random.choice(list(animals.items()))
    
    formatted_question = selected_question.format(animal=selected_animal.split()[0])
    
    # 남성과 여성 캐릭터 분리
    male_characters = [name for name, gender in characters.items() if gender == "male"]
    female_characters = [name for name, gender in characters.items() if gender == "female"]
    
    # 무작위로 첫 번째 화자의 성별을 선택하고, 두 번째 화자는 반대 성별에서 선택
    if random.choice([True, False]):
        speaker_a = random.choice(male_characters)
        speaker_b = random.choice(female_characters)
    else:
        speaker_a = random.choice(female_characters)
        speaker_b = random.choice(male_characters)
    
    key_expression = f"""
A: {speaker_a}: {formatted_question}
B: {speaker_b}: {selected_answer}
"""
    
    # 한국어 질문과 선택지 구성
    prompt = f"""
[영어 대화]
{key_expression}

[한국어 질문]
질문: {korean_question}
A. {korean_options[0]}
B. {korean_options[1]}
C. {korean_options[2]}
D. {korean_options[3]}
정답: {selected_answer.split()[-1]}
"""

    return prompt

def split_dialogue(text):
    lines = text.strip().split('\n')
    speakers = {}
    for line in lines:
        match = re.match(r'([A-Z]):\s*(.*)', line)
        if match:
            speaker, content = match.groups()
            if speaker not in speakers:
                speakers[speaker] = []
            speakers[speaker].append(content)
    return speakers

def text_to_speech(text, speaker):
    # 이 함수는 사전 정의된 캐릭터 성별에 맞춰 음성을 생성합니다.
    voice = "nova" if characters[speaker] == "female" else "echo"
    response = client.audio.speech.create(
        model="tts-1",
        voice=voice,
        input=text
    )
    
    audio_bytes = response.content
    audio_base64 = base64.b64encode(audio_bytes).decode()
    audio_tag = f'<audio controls><source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3"></audio>'
    
    return audio_tag

def generate_dialogue_audio(dialogue):
    speakers = split_dialogue(dialogue)
    audio_tags = []
    
    for speaker, lines in speakers.items():
        text = " ".join(lines)
        speaker_name = re.search(r'([A-Za-z]+):', lines[0]).group(1)  # 대화에서 화자 이름 추출
        audio_tag = text_to_speech(text, speaker_name)
        audio_tags.append(audio_tag)
    
    return "".join(audio_tags)

# Streamlit UI

# 메인 화면 구성
st.header("✨인공지능 영어듣기 퀴즈 선생님 퀴즐링🕵️‍♀️")
st.subheader("🦝동물의 생김새와 크기에 대한 영어듣기 퀴즈🦩")
st.divider()

# 세션 상태 초기화
if 'question_generated' not in st.session_state:
    st.session_state.question_generated = False

if st.button("새 문제 만들기"):
    # 세션 상태 초기화
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    
    full_content = generate_question()
    
    dialogue, question_part = full_content.split("[한국어 질문]")
    
    question_lines = question_part.strip().split("\n")
    question = question_lines[0].replace("질문:", "").strip() if question_lines else ""
    options = question_lines[1:5] if len(question_lines) > 1 else []
    correct_answer = ""
    
    for line in question_lines:
        if line.startswith("정답:"):
            correct_answer = line.replace("정답:", "").strip()
            break
    
    st.session_state.question = question
    st.session_state.dialogue = dialogue.strip()
    st.session_state.options = options
    st.session_state.correct_answer = correct_answer
    st.session_state.question_generated = True
    
    # 새 대화에 대한 음성 생성 (남녀 목소리 구분)
    st.session_state.audio_tags = generate_dialogue_audio(st.session_state.dialogue)
    
    # 페이지 새로고침
    st.rerun()

if 'question_generated' in st.session_state and st.session_state.question_generated:
    st.markdown("### 질문")
    st.write(st.session_state.question)
    
    # 저장된 음성 태그 사용
    st.markdown("### 대화 듣기")
    st.write("왼쪽부터 순서대로 들어보세요. 너무 빠르면 눈사람 버튼을 눌러 속도를 조절해보세요.")
    st.markdown(st.session_state.audio_tags, unsafe_allow_html=True)
    
    with st.form(key='answer_form'):
        selected_option = st.radio("정답을 선택하세요:", st.session_state.options, index=None)
        submit_button = st.form_submit_button(label='정답 확인')
        
        if submit_button:
            if selected_option:
                st.info(f"선택한 답: {selected_option}")
                if selected_option.strip() == st.session_state.correct_answer.strip():  
                    st.success("정답입니다!")
                    st.text(st.session_state.dialogue)
                else:
                    st.error(f"틀렸습니다. 정답은 {st.session_state.correct_answer}입니다.")
                    st.text(st.session_state.dialogue)
