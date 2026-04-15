import streamlit as st
from streamlit_gsheets import GSheetsConnection
import datetime
import pandas as pd
import base64
from PIL import Image
import io

st.set_page_config(page_title="오운완 인증💪", page_icon="🏋️‍♀️", layout="centered")

conn = st.connection("gsheets", type=GSheetsConnection)

def get_data():
    try:
        return conn.read(ttl=0)
    except:
        return pd.DataFrame(columns=["name", "date", "image", "comment"])

existing_data = get_data()

st.title("💪 오늘의 운동 완료 인증")
st.write("❗이번주 목표: 주 3일 30분 이상 운동완료❗")
st.write("❗미인증시: 벌금 1000원❗⭐매주 일요일 정산⭐")
st.write("🚫생리, 경조사, 늦은 가족모임, 여행 제외🚫")

with st.form("upload_form", clear_on_submit=True):
    st.header("오늘의 운동 인증하기")
    user_name = st.selectbox("누가 운동했나요?", ["가은", "소현"])
    date = st.date_input("날짜", datetime.date.today())
    uploaded_file = st.file_uploader("인증 사진을 올려주세요 📸", type=["jpg", "jpeg", "png"])
    comment = st.text_area("오늘 운동 소감🔥")
    submitted = st.form_submit_button("인증 완료!")

    if submitted:
        if uploaded_file is not None:
            try:
                # 📸 사진 압축 로직 추가
                img = Image.open(uploaded_file)
                img = img.convert("RGB") # RGBA일 경우 RGB로 변환
                
                # 가로 세로 비율 유지하며 크기 줄이기 (최대 500px)
                img.thumbnail((500, 500))
                
                # 압축된 이미지를 글자로 변환
                buffer = io.BytesIO()
                img.save(buffer, format="JPEG", quality=60) # 화질 60%로 압축
                encoded_img = base64.b64encode(buffer.getvalue()).decode()
                
                new_row = pd.DataFrame([{
                    "name": user_name, 
                    "date": date.strftime('%Y-%m-%d'), 
                    "image": encoded_img,
                    "comment": comment
                }])
                
                updated_df = pd.concat([existing_data, new_row], ignore_index=True)
                conn.update(data=updated_df)
                
                st.success("인증 완료! 이제 사진이 안전하게 저장되었습니다 👏")
                st.rerun()
            except Exception as e:
                st.error(f"업로드 중 오류가 발생했습니다: {e}")
        else:
            st.warning("사진을 꼭 업로드해주세요!")

st.divider()
st.header("🔥 오운완 피드")

if existing_data.empty or "name" not in existing_data.columns:
    st.info("아직 인증된 기록이 없습니다.")
else:
    for index, row in existing_data.iloc[::-1].iterrows():
        with st.expander(f"📅 {row['date']} - {row['name']}의 기록"):
            if pd.notnull(row['image']) and row['image'] != "":
                try:
                    st.image(base64.b64decode(row['image']), use_column_width=True)
                except:
                    st.write("⚠️ 사진을 불러올 수 없습니다.")
            st.write(f"💬 {row['comment']}")
