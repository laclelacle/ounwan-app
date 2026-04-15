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
        # 날짜 컬럼을 판다스 데이트타임 형식으로 변환 (계산을 위해)
        df['date'] = pd.to_datetime(df['date'])
        return df
    except:
        return pd.DataFrame(columns=["name", "date", "image", "comment"])

existing_data = get_data()

st.title("💪 오늘의 운동 완료 인증")
st.write("❗이번주 목표: 주 3일 30분 이상 운동완료❗")
st.write("❗미인증시: 벌금 1000원❗⭐매주 일요일 정산⭐")
st.write("🚫생리, 경조사, 늦은 가족모임, 여행 제외🚫")

# 3. 인증 기록 입력 폼 (이전과 동일)
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
                img = Image.open(uploaded_file)
                img = img.convert("RGB")
                img.thumbnail((500, 500))
                buffer = io.BytesIO()
                img.save(buffer, format="JPEG", quality=60)
                encoded_img = base64.b64encode(buffer.getvalue()).decode()
                
                new_row = pd.DataFrame([{
                    "name": user_name, 
                    "date": date, # datetime 객체로 저장
                    "image": encoded_img,
                    "comment": comment
                }])
                
                updated_df = pd.concat([existing_data, new_row], ignore_index=True)
                conn.update(data=updated_df)
                
                st.success("인증 완료! 주간 피드에 반영되었습니다 👏")
                st.rerun()
            except Exception as e:
                st.error(f"업로드 중 오류가 발생했습니다: {e}")
        else:
            st.warning("사진을 꼭 업로드해주세요!")

st.divider()

# 4. 🔥 주간별로 묶어서 보여주는 오운완 피드
st.header("🗓️ 주간 오운완 리포트")

if existing_data.empty or "name" not in existing_data.columns:
    st.info("아직 인증된 기록이 없습니다.")
else:
    # 데이터 정리: 날짜 기준으로 내림차순 정렬
    df_sorted = existing_data.sort_values(by="date", ascending=False)
    
    # 주차 계산 함수 (월요일 시작 기준)
    def get_week_label(d):
        monday = d - datetime.timedelta(days=d.weekday())
        sunday = monday + datetime.timedelta(days=6)
        return f"{monday.strftime('%m/%d')} ~ {sunday.strftime('%m/%d')} 주차 기록"

    # 주차별로 그룹화
    df_sorted['week'] = df_sorted['date'].apply(get_week_label)
    weeks = df_sorted['week'].unique()

    for week in weeks:
        # 최신 주차는 펼쳐두고, 지난 주차는 접어두기
        is_expanded = (week == weeks[0])
        
        with st.expander(f"📂 {week}", expanded=is_expanded):
            week_df = df_sorted[df_sorted['week'] == week]
            
            for _, row in week_df.iterrows():
                # 개별 기록 컨테이너
                with st.container():
                    date_str = row['date'].strftime('%Y-%m-%d')
                    st.subheader(f"✅ {date_str} - {row['name']}의 기록")
                    
                    if pd.notnull(row['image']) and row['image'] != "":
                        try:
                            st.image(base64.b64decode(row['image']), use_column_width=True)
                        except:
                            st.caption("⚠️ 이미지를 표시할 수 없습니다.")
                    
                    st.write(f"💬 {row['comment']}")
                    st.markdown("---") # 기록 간 구분선
