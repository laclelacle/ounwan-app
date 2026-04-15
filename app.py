import streamlit as st
from streamlit_gsheets import GSheetsConnection
import datetime
import pandas as pd
import base64
from PIL import Image
import io

# 1. 페이지 설정
st.set_page_config(page_title="오운완 인증💪", page_icon="🏋️‍♀️", layout="centered")

# 2. 구글 시트 연결
conn = st.connection("gsheets", type=GSheetsConnection)

def get_data():
    try:
        df = conn.read(ttl=0)
        # 날짜 컬럼을 판다스 데이트타임 형식으로 변환
        df['date'] = pd.to_datetime(df['date'])
        return df
    except:
        return pd.DataFrame(columns=["name", "date", "image", "comment"])

existing_data = get_data()

st.title("💪 오늘의 운동 완료 인증")
st.write("❗이번주 목표: 주 3일 30분 이상 운동완료❗")
st.write("❗미인증시: 벌금 1000원❗⭐매주 일요일 정산⭐")
st.write("🚫생리, 경조사, 늦은 가족모임, 여행 제외🚫")

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
            try:
                # 사진 압축
                img = Image.open(uploaded_file)
                img = img.convert("RGB")
                img.thumbnail((500, 500))
                buffer = io.BytesIO()
                img.save(buffer, format="JPEG", quality=60)
                encoded_img = base64.b64encode(buffer.getvalue()).decode()
                
                new_row = pd.DataFrame([{
                    "name": user_name, 
                    "date": pd.to_datetime(date), 
                    "image": encoded_img,
                    "comment": comment
                }])
                
                updated_df = pd.concat([existing_data, new_row], ignore_index=True)
                conn.update(data=updated_df)
                
                st.success("인증 완료! 피드가 업데이트되었습니다 👏")
                st.rerun()
            except Exception as e:
                st.error(f"업로드 중 오류가 발생했습니다: {e}")
        else:
            st.warning("사진을 꼭 업로드해주세요!")

st.divider()

# 4. 🔥 이중 접기 피드 (주차별 접기 > 일자별 접기)
st.header("🗓️ 주간 오운완 리포트")

if existing_data.empty or "name" not in existing_data.columns:
    st.info("아직 인증된 기록이 없습니다.")
else:
    # 데이터 정렬: 최신순
    df_sorted = existing_data.sort_values(by="date", ascending=False)
    
    def get_week_label(d):
        monday = d - datetime.timedelta(days=d.weekday())
        sunday = monday + datetime.timedelta(days=6)
        return f"{monday.strftime('%m/%d')} ~ {sunday.strftime('%m/%d')} 기록"

    df_sorted['week'] = df_sorted['date'].apply(get_week_label)
    weeks = df_sorted['week'].unique()

    for i, week in enumerate(weeks):
        # 1단계: 주차별 접기 (최신 주차만 기본으로 열어둠)
        with st.expander(f"📁 {week}", expanded=(i == 0)):
            week_df = df_sorted[df_sorted['week'] == week]
            dates_in_week = week_df['date'].unique()
            
            for j, d in enumerate(dates_in_week):
                d_str = pd.to_datetime(d).strftime('%Y-%m-%d')
                
                # 2단계: 일자별 접기 (최신 날짜만 기본으로 열어둠)
                # i==0(최신주차)이면서 j==0(최신날짜)일 때만 열려있게 설정
                is_day_expanded = (i == 0 and j == 0)
                
                with st.expander(f"📅 {d_str} 기록 보기", expanded=is_day_expanded):
                    day_df = week_df[week_df['date'] == d]
                    
                    for _, row in day_df.iterrows():
                        # 가은/소현 구분 아이콘
                        icon = "🦖" if row['name'] == "가은" else "🐣"
                        with st.chat_message("user", avatar=icon):
                            st.write(f"**{row['name']}의 기록**")
                            if pd.notnull(row['image']) and row['image'] != "":
                                try:
                                    st.image(base64.b64decode(row['image']), use_column_width=True)
                                except:
                                    st.caption("⚠️ 이미지를 불러올 수 없습니다.")
                            st.write(f"💬 {row['comment']}")
