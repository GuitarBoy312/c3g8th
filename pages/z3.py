import streamlit as st
from openai import OpenAI
import random
import base64
import re

# OpenAI 클라이언트 초기화
client = OpenAI(api_key=st.secrets["openai_api_key"])

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
    
    male_characters = [name for name, gender in characters.items() if gender == "male"]
    female_characters = [name for name, gender in characters.items() if gender == "female"]
    
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
    prompt = f"""{key_expression}을 생성해주세요. 
    그 후 대화 내용에 관한 객관식 질문을 한국어로 만들어주세요.  
    조건: 문제의 정답은 1개입니다.  
    영어 대화는 A와 B가 각각 1번씩 말하고 끝납니다.
    A는 다음과 같이 한문장을 말하세요.
    B는 다음과 같이 한문장을 말하세요.
    형식:
    [영어 대화]
    A: {speaker_a}: {formatted_question}
    B: {speaker_b}: {selected_answer}

    [한국어 질문]
    질문: {korean_question}
    A. {korean_options[0]}
    B. {korean_options[1]}
    C. {korean_options[2]}
    D. {korean_options[3]}
    정답: (정답 선택지)
    """

    response = client.chat.completions.create(
        model="gpt-4-0125-preview",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content

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
    voice = "alloy" if characters[speaker] == "female" else "echo"
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
        speaker_name = re.search(r'([A-Za-z]+):', lines[0]).group(1)
        audio_tag = text_to_speech(text, speaker_name)
        audio_tags.append(audio_tag)
    
    return "".join(audio_tags)

def generate_explanation(question, correct_answer, user_answer, dialogue):
    prompt = f"""
    다음 영어 대화와 관련된 질문에 대해 학생이 오답을 선택했습니다. 
    대화: {dialogue}
    질문: {question}
    정답: {correct_answer}
    학생의 답변: {user_answer}
    
    이 학생에게 그들의 답변이 왜 틀렸는지, 틀린 답변은 영어로 어떻게 표현할 수 있는지, 그리고 정답이 무엇인지 설명해주세요. 
    설명은 친절하고 격려하는 톤으로 작성해주세요. 
    대화의 내용을 참조하여 구체적으로 설명해주세요.
    """

    response = client.chat.completions.create(
        model="gpt-4-0125-preview",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content

# Streamlit UI
st.header("✨인공지능 영어듣기 퀴즈 선생님 퀴즐링🕵️‍♀️")
st.subheader("🦝동물의 생김새와 크기에 대한 영어듣기 퀴즈🦩")
st.divider()

with st.expander("❗❗ 글상자를 펼쳐 사용방법을 읽어보세요 👆✅", expanded=False):
    st.markdown(
    """     
    1️⃣ [새 문제 만들기] 버튼을 눌러 문제 만들기.<br>
    2️⃣ 재생 막대의 ▶ 버튼을 누르고 대화를 들어보기.<br>
    재생 막대의 오른쪽 스노우맨 버튼(점 세개)을 눌러 재생 속도를 조절할 수 있습니다.<br> 
    3️⃣ 정답을 선택하고 [정답 확인] 버튼 누르기.<br>
    4️⃣ 정답과 대화 스크립트 확인하기.<br>
    <br>
    🙏 퀴즐링은 완벽하지 않을 수 있어요.<br> 
    🙏 그럴 때에는 [새 제 만들기] 버튼을 눌러주세요.
    """
    ,  unsafe_allow_html=True)

if 'question_generated' not in st.session_state:
    st.session_state.question_generated = False

if st.button("새 문제 만들기"):
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    
    full_content = generate_question()
    
    dialogue, question_part = full_content.split("[한국어 질문]")
    
    question_lines = question_part.strip().split("\n")
    question = question_lines[1].replace("질문:", "").strip() if len(question_lines) > 1 else ""
    options = question_lines[2:6] if len(question_lines) > 2 else []
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
    
    st.session_state.audio_tags = generate_dialogue_audio(st.session_state.dialogue)
    
    st.rerun()

if 'question_generated' in st.session_state and st.session_state.question_generated:
    st.markdown("### 질문")
    st.write(st.session_state.question)
    
    st.markdown("### 대화 듣기")
    st.write("왼쪽부터 순서대로 들어보세요. 너무 빠르면 눈사람 버튼을 눌러 속도를 조절해보세요.")
    st.markdown(st.session_state.audio_tags, unsafe_allow_html=True)
    
    # 정답 옵션에서 정답 텍스트 제거하고 4개의 선택지 확보
    options = [opt for opt in st.session_state.options if not opt.startswith("정답:")]
    if len(options) < 4:
        options = ["A. 작다", "B. 크다", "C. 귀엽다", "D. 키가 크다"]
    
    with st.form(key='answer_form'):
        selected_option = st.radio("정답을 선택하세요:", options, index=None)
        submit_button = st.form_submit_button(label='정답 확인')
        
        if submit_button:
            if selected_option:
                st.info(f"선택한 답: {selected_option}")
                selected_answer = selected_option.split('.')[0].strip()
                correct_answer = st.session_state.correct_answer.strip()
                
                if selected_answer == correct_answer:  
                    st.success("정답입니다!")
                    st.text(st.session_state.dialogue)
                else:
                    st.error(f"틀렸습니다. 정답은 {st.session_state.correct_answer}입니다.")
                    st.text(st.session_state.dialogue)
                    
                    explanation = generate_explanation(
                        st.session_state.question,
                        st.session_state.correct_answer,
                        selected_option,
                        st.session_state.dialogue
                    )
                    st.markdown("### 오답 설명")
                    st.write(explanation)
            else:
                st.warning("답을 선택해주세요.")
