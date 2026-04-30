import streamlit as st
from streamlit_gsheets import GSheetsConnection
import datetime
import pandas as pd
import base64
from PIL import Image
import io

st.set_page_config(page_title="오운완 인증💪", page_icon="🏋️‍♀️", layout="centered")

conn = st.connection("gsheets", type=GSheetsConnection)

RECORDS_WS = "시트1"
EXCEPTIONS_WS = "exceptions"

if "editing_record_idx" not in st.session_state:
    st.session_state.editing_record_idx = None


def get_week_label(d):
    d = pd.to_datetime(d)
    monday = d - datetime.timedelta(days=d.weekday())
    sunday = monday + datetime.timedelta(days=6)
    return f"{monday.strftime('%m/%d')} ~ {sunday.strftime('%m/%d')} 기록"


def get_week_start(d):
    d = pd.to_datetime(d)
    monday = d - datetime.timedelta(days=d.weekday())
    return monday.strftime("%Y-%m-%d")


def encode_uploaded_image(uploaded_file):
    img = Image.open(uploaded_file)
    img = img.convert("RGB")
    img.thumbnail((500, 500))
    buffer = io.BytesIO()
    img.save(buffer, format="JPEG", quality=60)
    return base64.b64encode(buffer.getvalue()).decode()


def combine_links(*links):
    return "\n".join([link.strip() for link in links if link and link.strip() != ""])


def split_links(text):
    if not text or str(text).strip() == "":
        return []
    return [line.strip() for line in str(text).splitlines() if line.strip()]


def render_workout_links(urls_text):
    links = split_links(urls_text)
    if not links:
        return

    st.write("🏠💪 **따라한 홈트 영상**")
    for n, url in enumerate(links, start=1):
        st.markdown(f"{n}. [홈트 영상 보러가기]({url})")


def get_required_count(name, week_key, exceptions_data):
    target_rows = exceptions_data[
        (exceptions_data["name"] == name) &
        (exceptions_data["week"] == week_key)
    ]

    if target_rows.empty:
        return 3

    row = target_rows.iloc[0]

    if "target_count" not in row or str(row["target_count"]).strip() == "":
        if str(row["type"]).strip() == "인증 제외":
            return 0
        return 3

    try:
        return int(row["target_count"])
    except:
        return 3


def get_records_data():
    try:
        df = conn.read(worksheet=RECORDS_WS, ttl=0)

        if df.empty:
            return pd.DataFrame(columns=["name", "date", "image", "comment", "workout_urls"])

        if "workout_urls" not in df.columns:
            if "workout_url" in df.columns:
                df["workout_urls"] = df["workout_url"]
            else:
                df["workout_urls"] = ""

        expected_cols = ["name", "date", "image", "comment", "workout_urls"]
        for col in expected_cols:
            if col not in df.columns:
                df[col] = ""

        df["date"] = pd.to_datetime(df["date"])
        return df[expected_cols]

    except Exception:
        return pd.DataFrame(columns=["name", "date", "image", "comment", "workout_urls"])


def get_exceptions_data():
    try:
        df = conn.read(worksheet=EXCEPTIONS_WS, ttl=0)

        if df.empty:
            return pd.DataFrame(columns=["name", "week", "type", "target_count", "reason", "memo"])

        expected_cols = ["name", "week", "type", "target_count", "reason", "memo"]
        for col in expected_cols:
            if col not in df.columns:
                df[col] = ""

        return df[expected_cols]

    except Exception:
        return pd.DataFrame(columns=["name", "week", "type", "target_count", "reason", "memo"])


existing_data = get_records_data()
exceptions_data = get_exceptions_data()

st.title("💪 오늘의 운동 완료 인증")
st.write("❗이번주 기본 목표: 주 3일 30분 이상 운동완료❗")
st.write("❗미인증시: 벌금 1000원❗⭐매주 일요일 정산⭐")
st.write("🚫생리, 경조사, 늦은 가족모임, 여행, 병가, 몸살 제외/목표 조정 가능🚫")

st.divider()

left_col, right_col = st.columns(2)

with left_col:
    with st.form("upload_form", clear_on_submit=True):
        st.header("오늘의 운동 인증하기")

        user_name = st.selectbox("누가 운동했나요?", ["가은", "소현"])
        date = st.date_input("날짜", datetime.date.today())
        uploaded_file = st.file_uploader("인증 사진 📸", type=["jpg", "jpeg", "png"])
        comment = st.text_area("오늘 운동🔥")

        workout_url_1 = st.text_input("🏠💪 홈트 유튜브 링크 1")
        workout_url_2 = st.text_input("🏠💪 홈트 유튜브 링크 2")
        workout_url_3 = st.text_input("🏠💪 홈트 유튜브 링크 3")

        submitted = st.form_submit_button("인증 완료!")

        if submitted:
            if uploaded_file is not None:
                try:
                    encoded_img = encode_uploaded_image(uploaded_file)
                    workout_urls = combine_links(workout_url_1, workout_url_2, workout_url_3)

                    new_row = pd.DataFrame([{
                        "name": user_name,
                        "date": pd.to_datetime(date),
                        "image": encoded_img,
                        "comment": comment,
                        "workout_urls": workout_urls
                    }])

                    updated_df = pd.concat([existing_data, new_row], ignore_index=True)
                    conn.update(worksheet=RECORDS_WS, data=updated_df)

                    st.success("인증 완료!")
                    st.rerun()

                except Exception as e:
                    st.error(f"업로드 중 오류가 발생했습니다: {e}")
            else:
                st.warning("사진을 꼭 업로드해주세요!")


with right_col:
    with st.form("exception_form", clear_on_submit=True):
        st.header("🚫 인증 제외/목표 조정")

        exception_user = st.selectbox("누가 해당되나요?", ["가은", "소현"], key="exception_user")
        exception_date = st.date_input("해당 주간 날짜 선택", datetime.date.today(), key="exception_date")

        exception_type = st.radio(
            "처리 방식",
            ["이번 주 인증 제외", "이번 주 목표 횟수 조정"],
            key="exception_type"
        )

        if exception_type == "이번 주 인증 제외":
            target_count = 0
            exception_reason = st.selectbox(
                "사유",
                ["생리", "경조사", "늦은 가족모임", "여행", "병가", "몸살", "기타"],
                key="exception_reason_exempt"
            )
        else:
            target_count = st.selectbox(
                "이번 주 목표 횟수",
                [1, 2],
                key="target_count_adjust"
            )
            exception_reason = st.selectbox(
                "사유",
                ["몸살", "감기", "컨디션 난조", "병가", "생리", "기타"],
                key="exception_reason_adjust"
            )

        exception_memo = st.text_input("메모", key="exception_memo")

        exception_submitted = st.form_submit_button("등록")

        if exception_submitted:
            week_key = get_week_start(exception_date)

            already_exists = (
                (exceptions_data["name"] == exception_user)
                & (exceptions_data["week"] == week_key)
            ).any()

            if already_exists:
                st.warning("이미 해당 주간에 등록된 예외/목표 조정이 있습니다. 기존 항목을 취소하고 다시 등록해주세요.")
            else:
                new_exception = pd.DataFrame([{
                    "name": exception_user,
                    "week": week_key,
                    "type": exception_type,
                    "target_count": target_count,
                    "reason": exception_reason,
                    "memo": exception_memo.strip()
                }])

                updated_exceptions = pd.concat([exceptions_data, new_exception], ignore_index=True)
                conn.update(worksheet=EXCEPTIONS_WS, data=updated_exceptions)

                st.success("등록되었습니다.")
                st.rerun()

st.divider()

st.header("🗓️ 주간 오운완 리포트")

week_keys = set()

if not existing_data.empty:
    temp_records = existing_data.copy()
    temp_records["week_key"] = temp_records["date"].apply(get_week_start)
    for w in temp_records["week_key"].unique():
        week_keys.add(w)

if not exceptions_data.empty:
    for w in exceptions_data["week"].unique():
        if str(w).strip() != "":
            week_keys.add(w)

if len(week_keys) == 0:
    st.info("아직 인증된 기록이 없습니다.")
else:
    sorted_week_keys = sorted(list(week_keys), reverse=True)

    for i, week_key in enumerate(sorted_week_keys):
        week_start = pd.to_datetime(week_key)
        week_label = get_week_label(week_start)

        with st.expander(f"📁 {week_label}", expanded=(i == 0)):
            if not existing_data.empty:
                df_sorted = existing_data.copy()
                df_sorted["week_key"] = df_sorted["date"].apply(get_week_start)
                week_df = df_sorted[df_sorted["week_key"] == week_key].sort_values(
                    by="date", ascending=False
                )
            else:
                week_df = pd.DataFrame(columns=["name", "date", "image", "comment", "workout_urls", "week_key"])

            week_exceptions = exceptions_data[exceptions_data["week"] == week_key].copy()

            gaeun_count = len(week_df[week_df["name"] == "가은"])
            sohyeon_count = len(week_df[week_df["name"] == "소현"])

            gaeun_required = get_required_count("가은", week_key, exceptions_data)
            sohyeon_required = get_required_count("소현", week_key, exceptions_data)

            gaeun_status = (
                "인증 제외"
                if gaeun_required == 0
                else f"{gaeun_count}/{gaeun_required}회 인증"
            )
            sohyeon_status = (
                "인증 제외"
                if sohyeon_required == 0
                else f"{sohyeon_count}/{sohyeon_required}회 인증"
            )

            st.info(
                f"📊 **이번 주 인증 현황**\n\n"
                f"💎 **가은**: {gaeun_status}  |  🆑️ **소현**: {sohyeon_status}"
            )

            if not week_exceptions.empty:
                st.warning("🚫 **이번 주 예외/목표 조정 내역이 있습니다.**")
                for ex_idx, ex_row in week_exceptions.iterrows():
                    memo_text = f" / {ex_row['memo']}" if str(ex_row["memo"]).strip() != "" else ""

                    if str(ex_row["type"]).strip() == "이번 주 인증 제외":
                        st.write(f"- **{ex_row['name']}**: 인증 제외 / {ex_row['reason']}{memo_text}")
                    else:
                        st.write(
                            f"- **{ex_row['name']}**: 목표 {int(ex_row['target_count'])}회로 조정 / "
                            f"{ex_row['reason']}{memo_text}"
                        )

                    if st.button("예외/목표 조정 취소", key=f"delete_exception_{i}_{ex_idx}"):
                        updated_exceptions = exceptions_data.drop(index=ex_idx).reset_index(drop=True)
                        conn.update(worksheet=EXCEPTIONS_WS, data=updated_exceptions)
                        st.success("등록이 취소되었습니다.")
                        st.rerun()

            gaeun_done = gaeun_count >= gaeun_required
            sohyeon_done = sohyeon_count >= sohyeon_required

            if gaeun_done and sohyeon_done:
                st.write("🎉 **이번 주는 둘 다 정산 기준 통과!**")
            else:
                st.write("🏃 **목표까지 조금만 더! 일요일 정산 전까지 파이팅!**")

            st.divider()

            if week_df.empty:
                st.info("이 주간에는 운동 인증 기록이 없습니다.")
            else:
                dates_in_week = week_df["date"].unique()

                for j, d in enumerate(dates_in_week):
                    d_str = pd.to_datetime(d).strftime("%Y-%m-%d")

                    with st.expander(f"📅 {d_str} 기록 보기", expanded=(i == 0 and j == 0)):
                        day_df = week_df[week_df["date"] == d]

                        for idx, row in day_df.iterrows():
                            icon = "💎" if row["name"] == "가은" else "🆑️"

                            with st.chat_message("user", avatar=icon):
                                st.write(f"**{row['name']}의 기록**")

                                if pd.notnull(row["image"]) and row["image"] != "":
                                    try:
                                        st.image(base64.b64decode(row["image"]), use_container_width=True)
                                    except Exception:
                                        st.caption("⚠️ 이미지를 불러올 수 없습니다.")

                                if pd.notnull(row["comment"]) and row["comment"] != "":
                                    st.write(f"💬 {row['comment']}")

                                if pd.notnull(row["workout_urls"]) and str(row["workout_urls"]).strip() != "":
                                    render_workout_links(row["workout_urls"])

                                btn_col1, btn_col2 = st.columns(2)

                                with btn_col1:
                                    if st.button("✏️ 수정", key=f"edit_record_{idx}"):
                                        st.session_state.editing_record_idx = idx
                                        st.rerun()

                                with btn_col2:
                                    if st.button("🗑️ 이 기록 삭제", key=f"delete_record_{idx}"):
                                        deleted_df = existing_data.drop(index=idx).reset_index(drop=True)
                                        conn.update(worksheet=RECORDS_WS, data=deleted_df)

                                        if st.session_state.editing_record_idx == idx:
                                            st.session_state.editing_record_idx = None

                                        st.success("해당 기록이 삭제되었습니다.")
                                        st.rerun()

                                if st.session_state.editing_record_idx == idx:
                                    st.markdown("### ✏️ 기록 수정하기")

                                    existing_links = split_links(row["workout_urls"])
                                    existing_link_1 = existing_links[0] if len(existing_links) > 0 else ""
                                    existing_link_2 = existing_links[1] if len(existing_links) > 1 else ""
                                    existing_link_3 = existing_links[2] if len(existing_links) > 2 else ""

                                    with st.form(f"edit_form_{idx}"):
                                        edit_comment = st.text_area(
                                            "운동 내용 수정",
                                            value=str(row["comment"]) if pd.notnull(row["comment"]) else ""
                                        )

                                        edit_workout_url_1 = st.text_input(
                                            "🏠💪 홈트 유튜브 링크 1 수정",
                                            value=existing_link_1
                                        )
                                        edit_workout_url_2 = st.text_input(
                                            "🏠💪 홈트 유튜브 링크 2 수정",
                                            value=existing_link_2
                                        )
                                        edit_workout_url_3 = st.text_input(
                                            "🏠💪 홈트 유튜브 링크 3 수정",
                                            value=existing_link_3
                                        )

                                        edit_uploaded_file = st.file_uploader(
                                            "새 인증 사진으로 교체",
                                            type=["jpg", "jpeg", "png"],
                                            key=f"edit_file_{idx}"
                                        )

                                        save_edit = st.form_submit_button("💾 수정 저장")

                                    cancel_edit = st.button("취소", key=f"cancel_edit_{idx}")

                                    if save_edit:
                                        updated_df = existing_data.copy()
                                        updated_df.at[idx, "comment"] = edit_comment.strip()
                                        updated_df.at[idx, "workout_urls"] = combine_links(
                                            edit_workout_url_1,
                                            edit_workout_url_2,
                                            edit_workout_url_3
                                        )

                                        if edit_uploaded_file is not None:
                                            updated_df.at[idx, "image"] = encode_uploaded_image(edit_uploaded_file)

                                        conn.update(worksheet=RECORDS_WS, data=updated_df)
                                        st.session_state.editing_record_idx = None
                                        st.success("기록이 수정되었습니다.")
                                        st.rerun()

                                    if cancel_edit:
                                        st.session_state.editing_record_idx = None
                                        st.rerun()
