import streamlit as st
from openai import OpenAI
import random

# OpenAI 클라이언트 초기화
client = OpenAI(api_key=st.secrets["openai_api_key"])

# 단어 목록
words = {
    'big': '큰',
    'bird': '새',
    'cute': '귀여운',
    'elephant': '코끼리',
    'giraffe': '기린',
    'lion': '사자',
    'small': '작은',
    'tall': '키가 큰',
    'tiger': '호랑이',
    'to': '~로, ~에',
    'very': '매우',
    'zebra': '얼룩말',
    'zoo': '동물원',
    'milk': '우유',
    'too': '또한, 너무',
    'vegetable': '채소'
}

def generate_question():
    word, meaning = random.choice(list(words.items()))
    is_english_to_korean = random.choice([True, False])
    
    if is_english_to_korean:
        question = f"'{word}'의 한국어 뜻은 무엇인가요?"
        correct_answer = meaning
        other_options = [v for v in words.values() if v != meaning]
        options = random.sample(other_options, 3)
    else:
        question = f"'{meaning}'의 영어 단어는 무엇인가요?"
        correct_answer = word
        other_options = [k for k in words.keys() if k != word]
        options = random.sample(other_options, 3)

    options.append(correct_answer)
    random.shuffle(options)
    return question, options, correct_answer

# Streamlit UI

# 메인 화면 구성
st.header("✨인공지능 영어단어 퀴즈 선생님 퀴즐링🕵️‍♀️")
st.subheader("🦝동물의 생김새와 크기 영어단어 퀴즈🦩")
st.divider()

#확장 설명
with st.expander("❗❗ 글상자를 펼쳐 사용방법을 읽어보세요 👆✅", expanded=False):
    st.markdown(
    """     
    1️⃣ [새 문제 만들기] 버튼을 눌러 문제 만들기.<br>
    2️⃣ 질문을 읽고 정답을 선택하기.<br> 
    3️⃣ [정답 확인] 버튼 누르기.<br>
    4️⃣ 정답 확인하기.<br>
    <br>
    🙏 퀴즐링은 완벽하지 않을 수 있어요.<br> 
    🙏 그럴 때에는 [새 문제 만들기] 버튼을 눌러주세요.
    """
    ,  unsafe_allow_html=True)

# 세션 상태 초기화
if 'question_generated' not in st.session_state:
    st.session_state.question_generated = False

if st.button("새 문제 만들기"):
    # 세션 상태 초기화
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    
    question, options, correct_answer = generate_question()
    
    st.session_state.question = question
    st.session_state.options = options
    st.session_state.correct_answer = correct_answer
    st.session_state.question_generated = True
    
    # 페이지 새로고침
    st.rerun()

if 'question_generated' in st.session_state and st.session_state.question_generated:

    st.markdown("### 질문")
    st.write(st.session_state.question)
      
    with st.form(key='answer_form'):
        selected_option = st.radio("정답을 선택하세요:", st.session_state.options, index=None)
        submit_button = st.form_submit_button(label='정답 확인')

        if submit_button:
            if selected_option:
                st.info(f"선택한 답: {selected_option}")
                if selected_option.strip() == st.session_state.correct_answer.strip():  
                    st.success("정답입니다!")
                else:
                    st.error(f"틀렸습니다. 정답은 {st.session_state.correct_answer}입니다.")
            else:
                st.warning("답을 선택해주세요.")

# ... 기존 코드 ...
