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

# 세션 상태 초기화
if 'listening_quiz_total_questions' not in st.session_state:
    st.session_state.listening_quiz_total_questions = 0
if 'listening_quiz_correct_answers' not in st.session_state:
    st.session_state.listening_quiz_correct_answers = 0
if 'listening_quiz_current_question' not in st.session_state:
    st.session_state.listening_quiz_current_question = None

# 사이드바에 통계 표시 함수
def update_sidebar():
    st.sidebar.markdown("## 듣기 퀴즈 통계")
    st.sidebar.markdown(f"총 문제 수: {st.session_state.listening_quiz_total_questions}")
    st.sidebar.markdown(f"맞춘 문제 수: {st.session_state.listening_quiz_correct_answers}")
    if st.session_state.listening_quiz_total_questions > 0:
        accuracy = (st.session_state.listening_quiz_correct_answers / st.session_state.listening_quiz_total_questions) * 100
        st.sidebar.markdown(f"정확도: {accuracy:.2f}%")

# 메인 화면 구성
st.header("✨인공지능 영어듣기 퀴즈 선생님 퀴즐링🕵️‍♀️")
st.subheader("🦝동물의 생김새와 크기에 대한 영어듣기 퀴즈🦩")
st.divider()

# 현재 문제 표시
if st.session_state.listening_quiz_current_question:
    st.markdown("### 질문")
    st.write(st.session_state.question)
    
    st.markdown("### 대화 듣기")
    st.write("왼쪽부터 순서대로 들어보세요. 너무 빠르면 눈사람 버튼을 눌러 속도를 조절해보세요.")
    st.markdown(st.session_state.audio_tags, unsafe_allow_html=True)
    
    with st.form(key='answer_form'):
        selected_option = st.radio("정답을 선택하세요:", st.session_state.options, index=None)
        submit_button = st.form_submit_button(label='정답 확인')
        
        if submit_button:
            if selected_option:
                st.info(f"선택한 답: {selected_option}")
                correct_answer_text = st.session_state.correct_answer.strip()
                selected_option_text = selected_option.split('.')[-1].strip()
                
                st.session_state.listening_quiz_total_questions += 1
                if selected_option_text.lower() == correct_answer_text.lower():
                    st.success("정답입니다!")
                    st.session_state.listening_quiz_correct_answers += 1
                else:
                    st.error(f"틀렸습니다. 정답은 {st.session_state.correct_answer}입니다.")
                
                st.text(st.session_state.dialogue)
                
                if selected_option_text.lower() != correct_answer_text.lower():
                    explanation = generate_explanation(
                        st.session_state.question,
                        st.session_state.correct_answer,
                        selected_option,
                        st.session_state.dialogue
                    )
                    st.markdown("### 오답 설명")
                    st.write(explanation)
                
                update_sidebar()
                st.session_state.listening_quiz_current_question = None
            else:
                st.warning("답을 선택해주세요.")

# 사이드바 업데이트
update_sidebar()

# 새 문제 만들기 버튼 (맨 아래로 이동)
st.markdown("---")
if st.button("새 문제 만들기"):
    st.session_state.listening_quiz_current_question = None
    st.rerun()
