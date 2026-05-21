import streamlit as st
from streamlit_gsheets import GSheetsConnection
import datetime
import pandas as pd
import base64
from PIL import Image
import io
import calendar
from pathlib import Path

st.set_page_config(
    page_title="오운완 인증💪",
    page_icon="🏖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>

section[data-testid="stSidebar"] > div {
    display: block !important;
    visibility: visible !important;
}

button[kind="header"] {
    display: block !important;
    visibility: visible !important;
}
</style>
""", unsafe_allow_html=True)

ASSET_DIR = Path("assets")
DEER_SURF = ASSET_DIR / "deer_surf.png"
RJ_FLOAT = ASSET_DIR / "rj_float.png"
SUMMER_BANNER = ASSET_DIR / "summer_banner.png"

RECORDS_WS = "시트1"
EXCEPTIONS_WS = "exceptions"
IMAGE_SEPARATOR = "|||IMAGE|||"

conn = st.connection("gsheets", type=GSheetsConnection)

if "editing_record_idx" not in st.session_state:
    st.session_state.editing_record_idx = None


def img_to_base64(path):
    try:
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except Exception:
        return ""


deer_surf_b64 = img_to_base64(DEER_SURF)
rj_float_b64 = img_to_base64(RJ_FLOAT)
summer_banner_b64 = img_to_base64(SUMMER_BANNER)


st.markdown(f"""
<style>
header[data-testid="stHeader"] {{
    background: transparent;
}}

div[data-testid="stDecoration"] {{
    display: none;
}}

button[kind="header"] {{
    visibility: visible !important;
}}

.stApp {{
    background:
        linear-gradient(180deg, rgba(232,248,255,0.92), rgba(255,248,238,0.95), rgba(255,241,247,0.95));
}}

.block-container {{
    padding-top: 1rem;
    padding-bottom: 2rem;
}}

section[data-testid="stSidebar"] {{
    background:
        linear-gradient(180deg, rgba(225,245,255,0.95), rgba(255,244,249,0.95)),
        url("data:image/png;base64,{deer_surf_b64}");
    background-repeat: no-repeat;
    background-position: bottom center;
    background-size: 95%;
    border-right: 1px solid #c7eaff;
}}

h1, h2, h3 {{
    color: #073b73;
    font-weight: 900;
}}

div[data-testid="stForm"] {{
    background: rgba(255,255,255,0.94);
    padding: 28px;
    border-radius: 28px;
    box-shadow: 0 8px 24px rgba(64,151,198,0.18);
    border: 1.5px solid #bfe8ff;
}}

div[data-testid="stExpander"] {{
    background: rgba(255,255,255,0.94);
    border-radius: 22px;
    border: 1px solid #cfeeff;
    box-shadow: 0 6px 18px rgba(64,151,198,0.12);
    margin-bottom: 12px;
}}

.stButton>button {{
    background: linear-gradient(90deg, #63c7f7, #ff94ad);
    color: white;
    border: none;
    border-radius: 999px;
    font-weight: 900;
    padding: 0.55rem 1.3rem;
}}

.stButton>button:hover {{
    background: linear-gradient(90deg, #35b5f4, #ff7194);
    color: white;
    transform: scale(1.02);
}}

.stTextInput input,
.stTextArea textarea,
.stDateInput input {{
    border-radius: 15px !important;
    border: 1px solid #bfe8ff !important;
    background-color: #ffffff !important;
}}

div[data-baseweb="select"] > div {{
    border-radius: 15px !important;
    border-color: #bfe8ff !important;
}}

.custom-hero {{
    background-image:
        linear-gradient(90deg, rgba(255,255,255,0.15), rgba(255,255,255,0.15)),
        url("data:image/png;base64,{summer_banner_b64}");
    background-size: cover;
    background-position: center;
    border-radius: 32px;
    padding: 42px 36px;
    margin-bottom: 26px;
    min-height: 280px;
    box-shadow: 0 10px 30px rgba(64,151,198,0.2);
    border: 2px solid rgba(255,255,255,0.95);
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
}}

.hero-text-box {{
    background: rgba(255,255,255,0.72);
    padding: 14px 28px;
    border-radius: 999px;
    margin: 8px;
    color: #073b73;
    font-weight: 900;
    box-shadow: 0 4px 12px rgba(64,151,198,0.12);
}}

.hero-title {{
    font-size: 58px;
    font-weight: 1000;
    color: #0657a6;
    text-shadow: 2px 2px 0 white;
    margin-bottom: 12px;
}}

.calendar-table {{
    width: 100%;
    border-collapse: separate;
    border-spacing: 5px;
    table-layout: fixed;
}}

.calendar-table th {{
    background-color: #dff3ff;
    padding: 9px;
    text-align: center;
    font-size: 13px;
    border-radius: 12px;
    color: #073b73;
}}

.calendar-table td {{
    border: 1px solid #d7efff;
    background: rgba(255,255,255,0.88);
    vertical-align: top;
    height: 108px;
    padding: 7px;
    font-size: 13px;
    border-radius: 14px;
}}

.calendar-day {{
    font-weight: bold;
    margin-bottom: 5px;
    color: #073b73;
}}

.calendar-out {{
    color: #bbb;
    background-color: #f7fbff !important;
}}

.workout-badge {{
    display: block;
    margin-top: 4px;
    padding: 4px 6px;
    border-radius: 10px;
    background: linear-gradient(90deg, #e2f4ff, #ffe3ec);
    font-size: 12px;
    color: #073b73;
    font-weight: 800;
}}

.rj-decoration {{
    text-align: right;
    margin-top: -70px;
    margin-bottom: -10px;
}}

.rj-decoration img {{
    width: 160px;
}}
</style>
""", unsafe_allow_html=True)


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


def encode_uploaded_images(uploaded_files):
    return IMAGE_SEPARATOR.join([encode_uploaded_image(file) for file in uploaded_files])


def split_images(image_text):
    if not image_text or str(image_text).strip() == "":
        return []
    image_text = str(image_text)
    if IMAGE_SEPARATOR in image_text:
        return [img for img in image_text.split(IMAGE_SEPARATOR) if img.strip() != ""]
    return [image_text]


def render_images(image_text):
    for img in split_images(image_text):
        try:
            st.image(base64.b64decode(img), use_container_width=True)
        except Exception:
            st.caption("⚠️ 이미지를 불러올 수 없습니다.")


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


def get_required_count(name, week_key, targets_df):
    target_rows = targets_df[
        (targets_df["name"] == name) &
        (targets_df["week"] == week_key)
    ]
    if target_rows.empty:
        return 3
    try:
        return int(target_rows.iloc[0]["target_count"])
    except Exception:
        return 3


def safe_progress(count, required):
    if required == 0:
        return 1.0
    return min(count / required, 1.0)


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


def get_targets_data():
    try:
        df = conn.read(worksheet=EXCEPTIONS_WS, ttl=0)

        if df.empty:
            return pd.DataFrame(columns=["name", "week", "target_count", "reason", "memo"])

        expected_cols = ["name", "week", "target_count", "reason", "memo"]
        for col in expected_cols:
            if col not in df.columns:
                df[col] = ""

        return df[expected_cols]

    except Exception:
        return pd.DataFrame(columns=["name", "week", "target_count", "reason", "memo"])


def render_month_calendar(df):
    if df.empty:
        st.info("달력에 표시할 기록이 없습니다.")
        return

    st.subheader("🌞 월간 리포트 🌴")

    selected_month = st.date_input(
        "달력 기준 월 선택",
        datetime.date.today(),
        key="calendar_month"
    )

    year = selected_month.year
    month = selected_month.month

    month_df = df[
        (df["date"].dt.year == year) &
        (df["date"].dt.month == month)
    ]

    cal = calendar.Calendar(firstweekday=0)
    weeks = cal.monthdatescalendar(year, month)

    html = """
    <table class="calendar-table">
    <tr>
        <th>월</th>
        <th>화</th>
        <th>수</th>
        <th>목</th>
        <th>금</th>
        <th>토</th>
        <th>일</th>
    </tr>
    """

    for week in weeks:
        html += "<tr>"
        for day in week:
            is_current_month = day.month == month
            day_df = month_df[month_df["date"].dt.date == day]

            cell_class = "" if is_current_month else "calendar-out"
            html += f'<td class="{cell_class}">'
            html += f'<div class="calendar-day">{day.day}</div>'

            if not day_df.empty:
                for name in day_df["name"].unique():
                    count = len(day_df[day_df["name"] == name])
                    icon = "🐶" if name == "가은" else "🦌"
                    html += f'<span class="workout-badge">{icon} {name} {count}회</span>'

            html += "</td>"
        html += "</tr>"

    html += "</table>"
    st.markdown(html, unsafe_allow_html=True)


existing_data = get_records_data()
targets_data = get_targets_data()

st.sidebar.header("🎯 주간 목표 조정")

target_user = st.sidebar.selectbox("누구의 목표를 조정하나요?", ["가은", "소현"], key="target_user_select")
target_date = st.sidebar.date_input("해당 주간 날짜 선택", datetime.date.today(), key="target_date_input")
target_count = st.sidebar.selectbox("이번 주 목표 횟수", options=[0, 1, 2], index=2, key="target_count_select")
reason = st.sidebar.selectbox("사유", ["병가", "여행", "모임", "경조사", "생리", "시험 준비", "기타"], key="reason_select")
memo = st.sidebar.text_input("메모", key="memo_input")

if st.sidebar.button("🌸 목표 조정 등록", key="target_submit_button"):
    week_key = get_week_start(target_date)

    already_exists = (
        (targets_data["name"] == target_user)
        & (targets_data["week"] == week_key)
    ).any()

    if already_exists:
        st.sidebar.warning("이미 해당 주간에 목표 조정이 등록되어 있습니다. 기존 항목을 취소하고 다시 등록해주세요.")
    else:
        new_target = pd.DataFrame([{
            "name": target_user,
            "week": week_key,
            "target_count": target_count,
            "reason": reason,
            "memo": memo.strip() if memo else ""
        }])

        updated_targets = pd.concat([targets_data, new_target], ignore_index=True)
        conn.update(worksheet=EXCEPTIONS_WS, data=updated_targets)
        st.sidebar.success("목표 조정이 등록되었습니다.")
        st.rerun()


st.markdown("""
<div class="custom-hero">
    <div class="hero-title">💪 오늘의 운동 완료 인증</div>
    <div class="hero-text-box">❗ 기본 목표: 주 3일 30분 이상 운동완료 ❗</div>
    <div class="hero-text-box">❗ 미인증시: 벌금 1000원 ❗ ⭐ 매주 일요일 정산 ⭐</div>
    <div class="hero-text-box">🚫 병가, 여행, 모임, 경조사, 생리 등 사유 발생 시 목표 횟수 조정 가능 🚫</div>
</div>
""", unsafe_allow_html=True)

with st.form("upload_form", clear_on_submit=True):
    st.header("🌺 오늘의 운동 인증하기")

    col1, col2 = st.columns(2)
    with col1:
        user_name = st.selectbox("누가 운동했나요?", ["가은", "소현"], key="upload_user")
    with col2:
        date = st.date_input("날짜", datetime.date.today(), key="upload_date")

    uploaded_files = st.file_uploader(
        "인증 사진 📸",
        type=["jpg", "jpeg", "png"],
        accept_multiple_files=True,
        key="upload_files"
    )

    comment = st.text_area("오늘 운동🔥", key="upload_comment")

    link_col1, link_col2, link_col3 = st.columns(3)
    with link_col1:
        workout_url_1 = st.text_input("🏠💪 홈트 유튜브 링크 1", key="upload_url_1")
    with link_col2:
        workout_url_2 = st.text_input("🏠💪 홈트 유튜브 링크 2", key="upload_url_2")
    with link_col3:
        workout_url_3 = st.text_input("🏠💪 홈트 유튜브 링크 3", key="upload_url_3")

    submitted = st.form_submit_button("✅ 인증 완료!")

    if submitted:
        if uploaded_files:
            try:
                encoded_images = encode_uploaded_images(uploaded_files)
                workout_urls = combine_links(workout_url_1, workout_url_2, workout_url_3)

                new_row = pd.DataFrame([{
                    "name": user_name,
                    "date": pd.to_datetime(date),
                    "image": encoded_images,
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

st.divider()

st.header("🗓️ 주간 리포트")

calendar_col, report_col = st.columns([1, 1.2])

with calendar_col:
    render_month_calendar(existing_data)

with report_col:
    st.subheader("📋 주간 기록 리스트 ⭐")

    week_keys = set()

    if not existing_data.empty:
        temp_records = existing_data.copy()
        temp_records["week_key"] = temp_records["date"].apply(get_week_start)
        for w in temp_records["week_key"].unique():
            week_keys.add(w)

    if not targets_data.empty:
        for w in targets_data["week"].unique():
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

                week_targets = targets_data[targets_data["week"] == week_key].copy()

                gaeun_count = len(week_df[week_df["name"] == "가은"])
                sohyeon_count = len(week_df[week_df["name"] == "소현"])

                gaeun_required = get_required_count("가은", week_key, targets_data)
                sohyeon_required = get_required_count("소현", week_key, targets_data)

                gaeun_status = "인증 제외" if gaeun_required == 0 else f"{gaeun_count}/{gaeun_required}회 인증"
                sohyeon_status = "인증 제외" if sohyeon_required == 0 else f"{sohyeon_count}/{sohyeon_required}회 인증"

                st.info(
                    f"📊 **이번 주 인증 현황**\n\n"
                    f"🐶 **가은**: {gaeun_status}  |  🦌 **소현**: {sohyeon_status}"
                )

                st.write("🐶 가은 목표 달성률")
                if gaeun_required == 0:
                    st.progress(1.0)
                    st.caption("이번 주 인증 제외")
                else:
                    st.progress(safe_progress(gaeun_count, gaeun_required))
                    st.caption(f"{gaeun_count}/{gaeun_required}회 완료")

                st.write("🦌 소현 목표 달성률")
                if sohyeon_required == 0:
                    st.progress(1.0)
                    st.caption("이번 주 인증 제외")
                else:
                    st.progress(safe_progress(sohyeon_count, sohyeon_required))
                    st.caption(f"{sohyeon_count}/{sohyeon_required}회 완료")

                if not week_targets.empty:
                    st.warning("🎯 **이번 주 목표 조정 내역이 있습니다.**")

                    for target_idx, target_row in week_targets.iterrows():
                        try:
                            target_value = int(target_row["target_count"])
                        except Exception:
                            target_value = 3

                        memo_value = target_row["memo"]
                        memo_text = f" / {memo_value}" if pd.notnull(memo_value) and str(memo_value).strip() != "" else ""

                        if target_value == 0:
                            st.write(f"- **{target_row['name']}**: 인증 제외 / {target_row['reason']}{memo_text}")
                        else:
                            st.write(f"- **{target_row['name']}**: 목표 {target_value}회 / {target_row['reason']}{memo_text}")

                        if st.button("목표 조정 취소", key=f"delete_target_{i}_{target_idx}"):
                            updated_targets = targets_data.drop(index=target_idx).reset_index(drop=True)
                            conn.update(worksheet=EXCEPTIONS_WS, data=updated_targets)
                            st.success("목표 조정이 취소되었습니다.")
                            st.rerun()

                if gaeun_count >= gaeun_required and sohyeon_count >= sohyeon_required:
                    st.write("🎉 **이번 주는 둘 다 정산 기준 통과!**")
                else:
                    st.write("🏃 **목표까지 조금만 더! 일요일 정산 전까지 파이팅!**")

                if rj_float_b64:
                    st.markdown(
                        f"""
                        <div class="rj-decoration">
                            <img src="data:image/png;base64,{rj_float_b64}">
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

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
                                icon = "🐶" if row["name"] == "가은" else "🦌"

                                with st.chat_message("user", avatar=icon):
                                    st.write(f"**{row['name']}의 기록**")

                                    if pd.notnull(row["image"]) and row["image"] != "":
                                        render_images(row["image"])

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

                                            edit_workout_url_1 = st.text_input("🏠💪 홈트 유튜브 링크 1 수정", value=existing_link_1)
                                            edit_workout_url_2 = st.text_input("🏠💪 홈트 유튜브 링크 2 수정", value=existing_link_2)
                                            edit_workout_url_3 = st.text_input("🏠💪 홈트 유튜브 링크 3 수정", value=existing_link_3)

                                            edit_uploaded_files = st.file_uploader(
                                                "새 인증 사진으로 교체",
                                                type=["jpg", "jpeg", "png"],
                                                accept_multiple_files=True,
                                                key=f"edit_files_{idx}"
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

                                            if edit_uploaded_files:
                                                updated_df.at[idx, "image"] = encode_uploaded_images(edit_uploaded_files)

                                            conn.update(worksheet=RECORDS_WS, data=updated_df)
                                            st.session_state.editing_record_idx = None
                                            st.success("기록이 수정되었습니다.")
                                            st.rerun()

                                        if cancel_edit:
                                            st.session_state.editing_record_idx = None
                                            st.rerun()
