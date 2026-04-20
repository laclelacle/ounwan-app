import streamlit as st
from streamlit_gsheets import GSheetsConnection
import streamlit.components.v1 as components
import datetime
import pandas as pd
import base64
from PIL import Image
import io

# 1. 페이지 설정
st.set_page_config(page_title="오운완 인증💪", page_icon="🏋️‍♀️", layout="centered")

# 2. 구글 시트 연결
conn = st.connection("gsheets", type=GSheetsConnection)

# 3. 사용 시트 이름
# ⚠️ 아래 RECORDS_WS는 네 기존 운동 기록이 들어있는 "실제 시트 탭 이름"으로 맞춰야 함
RECORDS_WS = "운동기록"
MUSIC_WS = "music_links"

# 4. 운동 기록 불러오기
def get_records_data():
    try:
        df = conn.read(worksheet=RECORDS_WS, ttl=0)

        if df.empty:
            return pd.DataFrame(columns=["name", "date", "image", "comment", "workout_url"])

        expected_cols = ["name", "date", "image", "comment", "workout_url"]
        for col in expected_cols:
            if col not in df.columns:
                df[col] = ""

        df["date"] = pd.to_datetime(df["date"])
        return df[expected_cols]

    except:
        return pd.DataFrame(columns=["name", "date", "image", "comment", "workout_url"])

# 5. 음악 링크 기록 불러오기
def get_music_data():
    try:
        df = conn.read(worksheet=MUSIC_WS, ttl=0)

        if df.empty:
            return pd.DataFrame(columns=["name", "week", "music_url"])

        expected_cols = ["name", "week", "music_url"]
        for col in expected_cols:
            if col not in df.columns:
                df[col] = ""

        return df[expected_cols]

    except:
        return pd.DataFrame(columns=["name", "week", "music_url"])

existing_data = get_records_data()
music_data = get_music_data()

# 6. 주차 라벨 함수
def get_week_label(d):
    monday = d - datetime.timedelta(days=d.weekday())
    sunday = monday + datetime.timedelta(days=6)
    return f"{monday.strftime('%m/%d')} ~ {sunday.strftime('%m/%d')} 기록"

# 7. 음악 플레이어 렌더링 함수
def render_music_player(url):
    if not url or str(url).strip() == "":
        return

    url = str(url).strip()

    # 유튜브
    if "youtube.com" in url or "youtu.be" in url:
        st.video(url)

    # 스포티파이
    elif "open.spotify.com" in url:
        embed_url = url.replace("open.spotify.com/", "open.spotify.com/embed/")

        if "?" in embed_url:
            embed_url = embed_url.split("?")[0]

        components.html(
            f"""
            <iframe
                src="{embed_url}"
                width="100%"
                height="152"
                frameborder="0"
                allowfullscreen=""
                allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture">
            </iframe>
            """,
            height=180,
        )
    else:
        st.warning("유튜브 또는 스포티파이 링크만 넣어주세요.")

# 8. 홈트 링크 표시 함수
def render_workout_link(url):
    if not url or str(url).strip() == "":
        return

    url = str(url).strip()

    if "youtube.com" in url or "youtu.be" in url:
        st.markdown(f"🏠 [오늘 한 홈트 영상 보러가기]({url})")
    else:
        st.markdown(f"🏠 [운동 링크 보기]({url})")

# 9. 제목 및 안내문
st.title("💪 오늘의 운동 완료 인증")
st.write("❗이번주 목표: 주 3일 30분 이상 운동완료❗")
st.write("❗미인증시: 벌금 1000원❗⭐매주 일요일 정산⭐")
st.write("🚫생리, 경조사, 늦은 가족모임, 여행 제외🚫")

# 10. 인증 기록 입력 폼
with st.form("upload_form", clear_on_submit=True):
    st.header("오늘의 운동 인증하기")

    user_name = st.selectbox("누가 운동했나요?", ["가은", "소현"])
    date = st.date_input("날짜", datetime.date.today())
    uploaded_file = st.file_uploader("인증 사진 📸", type=["jpg", "jpeg", "png"])
    comment = st.text_area("오늘 운동🔥(예: 땅끄부부 칼소폭 30분 / 탄천 걷기 30분)")
    workout_url = st.text_input("🏠 따라한 홈트 유튜브 링크 (선택)")
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
                    "date": pd.to_datetime(date),
                    "image": encoded_img,
                    "comment": comment,
                    "workout_url": workout_url.strip()
                }])

                updated_df = pd.concat([existing_data, new_row], ignore_index=True)
                conn.update(worksheet=RECORDS_WS, data=updated_df)

                st.success("인증 완료! 주간 리포트를 확인해 보세요 👏")
                st.rerun()

            except Exception as e:
                st.error(f"업로드 중 오류가 발생했습니다: {e}")
        else:
            st.warning("사진을 꼭 업로드해주세요!")

st.divider()

# 11. 주간 리포트
st.header("🗓️ 주간 오운완 리포트")

if existing_data.empty or "name" not in existing_data.columns:
    st.info("아직 인증된 기록이 없습니다.")
else:
    df_sorted = existing_data.sort_values(by="date", ascending=False).copy()
    df_sorted["week"] = df_sorted["date"].apply(get_week_label)
    weeks = df_sorted["week"].unique()

    for i, week in enumerate(weeks):
        with st.expander(f"📁 {week}", expanded=(i == 0)):
            week_df = df_sorted[df_sorted["week"] == week]

            gaeun_count = len(week_df[week_df["name"] == "가은"])
            sohyeon_count = len(week_df[week_df["name"] == "소현"])

            st.info(
                f"📊 **이번 주 인증 현황**\n\n"
                f"💎 **가은**: {gaeun_count}회 인증  |  🆑️ **소현**: {sohyeon_count}회 인증"
            )

            # 목표 달성 여부 메시지
            if gaeun_count >= 3 and sohyeon_count >= 3:
                st.write("🎉 **둘 다 이번 주 목표 달성! 우리 쫌 하는듯!**")
            else:
                st.write("🏃 **목표까지 조금만 더! 일요일 정산 전까지 파이팅!**")

                st.subheader("🎧 운동하면서 들은 음악 올리기")

                music_user = st.selectbox(
                    "누가 음악을 올리나요?",
                    ["가은", "소현"],
                    key=f"music_user_{i}"
                )

                music_url = st.text_input(
                    "🎵 운동하면서 들은 음악 링크 (유튜브 / 스포티파이)",
                    key=f"music_url_{i}",
                    placeholder="예: https://www.youtube.com/watch?v=... 또는 https://open.spotify.com/track/..."
                )

                col1, col2 = st.columns([1, 1])

                with col1:
                    if st.button("🎵 링크 저장", key=f"save_music_{i}"):
                        if music_url.strip() == "":
                            st.warning("링크를 먼저 입력해주세요!")
                        else:
                            new_music_row = pd.DataFrame([{
                                "name": music_user,
                                "week": week,
                                "music_url": music_url.strip()
                            }])

                            updated_music_df = pd.concat([music_data, new_music_row], ignore_index=True)
                            conn.update(worksheet=MUSIC_WS, data=updated_music_df)
                            st.success("음악 링크가 저장되었어요!")
                            st.rerun()

                with col2:
                    if music_url.strip() != "":
                        st.caption("미리보기")
                        render_music_player(music_url)

                # 이번 주 음악 링크 모아보기
                week_music_df = music_data[music_data["week"] == week].copy()

                with st.expander("📚 지금까지 올린 음악 링크 모아보기", expanded=False):
                    if week_music_df.empty:
                        st.info("아직 저장된 음악 링크가 없습니다.")
                    else:
                        week_music_df = week_music_df.iloc[::-1]

                        for m_idx, m_row in week_music_df.iterrows():
                            st.markdown(f"**{m_row['name']}**")
                            st.caption(m_row["music_url"])
                            render_music_player(m_row["music_url"])

                            if st.button("🗑️ 이 음악 링크 삭제", key=f"delete_music_{i}_{m_idx}"):
                                try:
                                    deleted_music_df = music_data.drop(index=m_idx).reset_index(drop=True)
                                    conn.update(worksheet=MUSIC_WS, data=deleted_music_df)
                                    st.success("음악 링크가 삭제되었습니다.")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"음악 링크 삭제 중 오류가 발생했습니다: {e}")

                            st.divider()

            st.divider()

            # 날짜별 기록 보기
            dates_in_week = week_df["date"].unique()

            for j, d in enumerate(dates_in_week):
                d_str = pd.to_datetime(d).strftime("%Y-%m-%d")
                is_day_expanded = (i == 0 and j == 0)

                with st.expander(f"📅 {d_str} 기록 보기", expanded=is_day_expanded):
                    day_df = week_df[week_df["date"] == d]

                    for idx, row in day_df.iterrows():
                        icon = "💎" if row["name"] == "가은" else "🆑️"

                        with st.chat_message("user", avatar=icon):
                            st.write(f"**{row['name']}의 기록**")

                            # 이미지 출력
                            if pd.notnull(row["image"]) and row["image"] != "":
                                try:
                                    st.image(base64.b64decode(row["image"]), use_container_width=True)
                                except:
                                    st.caption("⚠️ 이미지를 불러올 수 없습니다.")

                            # 운동 내용
                            if pd.notnull(row["comment"]) and row["comment"] != "":
                                st.write(f"💬 {row['comment']}")

                            # 홈트 링크 출력
                            if pd.notnull(row["workout_url"]) and str(row["workout_url"]).strip() != "":
                                render_workout_link(row["workout_url"])

                            # 운동 기록 삭제 버튼
                            if st.button("🗑️ 이 기록 삭제", key=f"delete_record_{idx}"):
                                try:
                                    deleted_df = existing_data.drop(index=idx).reset_index(drop=True)
                                    conn.update(worksheet=RECORDS_WS, data=deleted_df)
                                    st.success("해당 기록이 삭제되었습니다.")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"삭제 중 오류가 발생했습니다: {e}")
