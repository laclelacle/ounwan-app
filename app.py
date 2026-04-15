import streamlit as st
import datetime

# 1. 페이지 기본 설정
st.set_page_config(page_title="오운완 인증💪", page_icon="🏋️‍♀️", layout="centered")

st.title("💪 오늘의 운동 완료 인증")
st.write("❗이번주 목표: 주 3일 30분 이상 운동완료❗")
st.write("❗미인증시: 벌금 1000원❗⭐매주 일요일 정산⭐")
st.write("🚫생리, 경조사, 늦은 가족모임, 여행 제외🚫")

# 2. 데이터 임시 저장소 초기화 (앱이 실행되는 동안만 유지됨)
if 'records' not in st.session_state:
    st.session_state.records = []

# 3. 인증 기록 입력 폼 만들기
with st.form("upload_form", clear_on_submit=True):
    st.header("오늘의 운동 인증하기")
    
    # 작성자 선택 
    user_name = st.selectbox("누가 운동했나요?", ["가은", "소현"])
    
    # 날짜 선택 (기본값은 오늘)
    date = st.date_input("날짜", datetime.date.today())
    
    # 사진 업로드 기능
    uploaded_file = st.file_uploader("인증 사진을 올려주세요 📸", type=["jpg", "jpeg", "png"])
    
    # 간단한 코멘트
    comment = st.text_area("오늘 운동은? (예: 땅끄부부 칼폭소 30분🔥/ 탄천 30분 운동🏃‍♀️‍➡️)")
    
    # 폼 제출 버튼
    submitted = st.form_submit_button("인증 완료!")
    
    # 버튼이 눌렸을 때의 동작
    if submitted:
        if uploaded_file is not None:
            # 입력된 데이터를 세션 상태에 추가
            st.session_state.records.append({
                "name": user_name,
                "date": date,
                "image": uploaded_file,
                "comment": comment
            })
            st.success("인증 완료! 오늘도 고생하셨습니다 👏")
        else:
            # 사진을 안 올렸을 경우 경고
            st.warning("사진을 꼭 업로드해주세요!")

st.divider() # 구분선

# 4. 오운완 피드 (주차별 기록 보여주기)
st.header("🔥 오운완 피드")

if not st.session_state.records:
    st.info("아직 인증된 기록이 없습니다. 첫 번째 인증을 남겨주세요!")
else:
    # 1단계: 기록들을 주차별로 분류할 빈 딕셔너리 만들기
    records_by_week = {}
    
    # 2단계: 모든 기록을 확인하며 어느 주차에 속하는지 계산하여 분류하기
    for record in st.session_state.records:
        date_obj = record['date']
        monday = date_obj - datetime.timedelta(days=date_obj.weekday())
        sunday = monday + datetime.timedelta(days=6)
        week_label = f"{monday.strftime('%m/%d')} ~ {sunday.strftime('%m/%d')} 주차"
        
        if week_label not in records_by_week:
            records_by_week[week_label] = []
        records_by_week[week_label].append(record)
        
    # 3단계: 화면에 출력하기 (최신 주차가 위로 올라오도록 정렬)
    sorted_weeks = sorted(records_by_week.keys(), reverse=True)
    
    for week in sorted_weeks:
        is_expanded = (week == sorted_weeks[0]) 
        
        with st.expander(f"📅 {week} 인증 기록 보기", expanded=is_expanded):
            for record in reversed(records_by_week[week]):
                with st.container():
                    st.subheader(f"{record['date']} - {record['name']}의 기록")
                    st.image(record['image'], use_column_width=True)
                    st.write(f"💬 {record['comment']}")
                    
                    # 💡 새로 추가된 부분: 삭제 버튼
                    # 버튼의 고유 ID(key)로 메모리 주소인 id()를 사용해 에러를 방지합니다.
                    if st.button("🗑️ 이 기록 삭제하기", key=f"del_{id(record)}"):
                        # 저장소에서 해당 기록을 찾아 지웁니다.
                        st.session_state.records.remove(record)
                        # 삭제된 상태를 화면에 즉시 반영하기 위해 새로고침합니다.
                        st.rerun() 
                        
                    st.divider()