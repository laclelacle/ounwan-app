import streamlit as st
from streamlit_gsheets import GSheetsConnection
import datetime
import pandas as pd
import base64

# 1. 페이지 설정
st.set_page_config(page_title="오운완 인증💪", page_icon="🏋️‍♀️", layout="centered")

# 2. 구글 시트 연결
conn = st.connection("gsheets", type=GSheetsConnection)

# 데이터 불러오기 함수
def get_data():
    try:
        # 시트에서 데이터를 읽어옵니다. (ttl=0은 캐시를 쓰지 않고 매번 새로 읽는다는 뜻)
        return conn.read(ttl=0)
    except:
        # 시트가 아예 비어있을 경우를 대비한 기본 틀
        return pd.DataFrame(columns=["name", "date", "image", "comment"])

existing_data = get_data()

st.title("💪 오늘의 운동 완료 인증")
st.write("❗이번주 목표: 주 3일 30분 이상 운동완료❗")
st.write("❗미인증시: 벌금 1000원 | 일요일 정산❗")

# 3. 인증 기록 입력 폼
with st.form("upload_form", clear_on_submit=True):
    st.header("오늘의 운동 인증하기")
    
    user_name = st.selectbox("누가 운동했나요?", ["가은", "소현"])
    date = st.date_input("날짜", datetime.date.today())
    uploaded_file = st.file_uploader("인증 사진을 올려주세요 📸", type=["jpg", "jpeg", "png"])
    comment = st.text_area("오늘 운동 소감🔥")
    
    submitted = st.form_submit_button("인증 완료!")

    if submitted:
        if uploaded_file is not None:
            # 사진 파일을 글자(Base64)로 변환하여 시트에 저장할 준비를 합니다.
            img_bytes = uploaded_file.read()
            encoded_img = base64.b64encode(img_bytes).decode()
            
            # 새로운 기록 한 줄 만들기
            new_row = pd.DataFrame([{
                "name": user_name, 
                "date": date.strftime('%Y-%m-%d'), 
                "image": encoded_img,
                "comment": comment
            }])
            
            # 기존 데이터에 합치기
            updated_df = pd.concat([existing_data, new_row], ignore_index=True)
            
            # 구글 시트에 최종 저장!
            conn.update(data=updated_df)
            
            st.success("인증 완료! 이제 소현님 화면에도 이 사진이 보일 거예요 👏")
            st.rerun() # 화면 새로고침해서 결과 바로 보여주기
        else:
            st.warning("사진을 꼭 업로드해주세요!")

st.divider()

# 4. 오운완 피드 (실시간 공유 화면)
st.header("🔥 오운완 피드")

if existing_data.empty or "name" not in existing_data.columns:
    st.info("아직 인증된 기록이 없습니다. 첫 번째 인증을 남겨주세요!")
else:
    # 가장 최근 기록이 위로 오도록 역순으로 보여줍니다.
    for index, row in existing_data.iloc[::-1].iterrows():
        # 날짜를 기준으로 주차 계산 (정산용)
        try:
            date_obj = datetime.datetime.strptime(str(row['date']), '%Y-%m-%d')
            monday = date_obj - datetime.timedelta(days=date_obj.weekday())
            sunday = monday + datetime.timedelta(days=6)
            week_label = f"{monday.strftime('%m/%d')} ~ {sunday.strftime('%m/%d')} 주차"
        except:
            week_label = "날짜 정보 없음"

        with st.expander(f"📅 {row['date']} - {row['name']}의 기록"):
            # 저장된 글자 데이터를 다시 사진으로 바꿔서 보여줍니다.
            if pd.notnull(row['image']) and row['image'] != "":
                st.image(base64.b64decode(row['image']), use_column_width=True)
            st.write(f"💬 {row['comment']}")
