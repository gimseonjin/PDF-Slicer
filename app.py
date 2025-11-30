import io
import zipfile
import streamlit as st
from pypdf import PdfReader, PdfWriter
from pdf2image import convert_from_bytes

st.set_page_config(page_title="PDF 분할", page_icon="📄", layout="wide")
st.title("PDF 분할기")


COLORS = ["#FF6B6B", "#4ECDC4", "#45B7D1", "#96CEB4", "#FFEAA7", "#DDA0DD", "#98D8C8", "#F7DC6F"]

@st.cache_data
def get_thumbnails(pdf_bytes):
    images = convert_from_bytes(pdf_bytes, dpi=80)
    return images

uploaded_file = st.file_uploader("PDF 파일을 업로드하세요", type="pdf")

if uploaded_file:
    pdf_bytes = uploaded_file.read()
    uploaded_file.seek(0)
    pdf_reader = PdfReader(uploaded_file)
    total_pages = len(pdf_reader.pages)

    st.info(f"총 페이지 수: **{total_pages}**")

    if "sections" not in st.session_state:
        st.session_state.sections = [{"start": 1, "end": total_pages, "name": "section_1"}]

    with st.spinner("썸네일 생성 중..."):
        thumbnails = get_thumbnails(pdf_bytes)

    left_col, right_col = st.columns([1, 2])

    with left_col:
        st.subheader("구간 설정")

        btn_col1, btn_col2 = st.columns([1, 1])
        with btn_col1:
            if st.button("구간 추가", use_container_width=True):
                idx = len(st.session_state.sections) + 1
                st.session_state.sections.append({"start": 1, "end": total_pages, "name": f"section_{idx}"})
                st.rerun()
        with btn_col2:
            if st.button("구간 삭제", use_container_width=True) and len(st.session_state.sections) > 1:
                st.session_state.sections.pop()
                st.rerun()

        with st.container(height=500):
            for i, section in enumerate(st.session_state.sections):
                color = COLORS[i % len(COLORS)]
                st.markdown(f"**구간 {i+1}** <span style='color:{color};'>●</span>", unsafe_allow_html=True)

                c1, c2 = st.columns(2)
                with c1:
                    section["start"] = st.number_input(
                        "시작",
                        min_value=1,
                        max_value=total_pages,
                        value=section["start"],
                        key=f"start_{i}"
                    )
                with c2:
                    section["end"] = st.number_input(
                        "끝",
                        min_value=1,
                        max_value=total_pages,
                        value=section["end"],
                        key=f"end_{i}"
                    )
                section["name"] = st.text_input(
                    "파일명",
                    value=section["name"],
                    key=f"name_{i}"
                )
                st.divider()

        if st.button("분할하기", type="primary", use_container_width=True):
            errors = []
            for i, section in enumerate(st.session_state.sections):
                if section["start"] > section["end"]:
                    errors.append(f"구간 {i+1}: 시작 > 끝")
                if not section["name"].strip():
                    errors.append(f"구간 {i+1}: 파일명 필요")

            if errors:
                for err in errors:
                    st.error(err)
            else:
                zip_buffer = io.BytesIO()
                with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
                    for section in st.session_state.sections:
                        pdf_writer = PdfWriter()
                        for page_num in range(section["start"] - 1, section["end"]):
                            pdf_writer.add_page(pdf_reader.pages[page_num])

                        pdf_buffer = io.BytesIO()
                        pdf_writer.write(pdf_buffer)
                        pdf_buffer.seek(0)

                        filename = section["name"].strip()
                        if not filename.endswith(".pdf"):
                            filename += ".pdf"
                        zip_file.writestr(filename, pdf_buffer.getvalue())

                zip_buffer.seek(0)
                st.success("분할 완료!")
                st.download_button(
                    label="ZIP 다운로드",
                    data=zip_buffer,
                    file_name="split_pdfs.zip",
                    mime="application/zip",
                    use_container_width=True
                )

    with right_col:
        st.subheader("미리보기")

        page_to_sections = {}
        for i, section in enumerate(st.session_state.sections):
            for p in range(section["start"], section["end"] + 1):
                if p not in page_to_sections:
                    page_to_sections[p] = []
                page_to_sections[p].append(i)

        with st.container(height=550):
            cols_per_row = 4
            for row_start in range(0, total_pages, cols_per_row):
                cols = st.columns(cols_per_row)
                for col_idx, col in enumerate(cols):
                    page_num = row_start + col_idx + 1
                    if page_num > total_pages:
                        break

                    section_indices = page_to_sections.get(page_num, [])
                    if section_indices:
                        color = COLORS[section_indices[0] % len(COLORS)]
                    else:
                        color = "#ddd"

                    with col:
                        st.image(thumbnails[page_num - 1], use_container_width=True)
                        st.markdown(f"<div style='text-align:center; border-top: 4px solid {color}; padding-top: 5px;'><b>{page_num}</b></div>", unsafe_allow_html=True)
