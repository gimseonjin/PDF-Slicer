# PDF Slicer

PDF 파일을 원하는 구간별로 나눠서 다운로드할 수 있는 웹 도구.

## 기능

- PDF 업로드 후 페이지 썸네일 미리보기
- 여러 구간 설정 (시작 페이지 ~ 끝 페이지)
- 구간별로 다른 파일명 지정
- 분할된 PDF들을 ZIP으로 한번에 다운로드

## 사용 예시

- 책 PDF에서 특정 챕터만 추출
- 스캔 문서에서 필요한 페이지만 분리
- 긴 PDF를 여러 파트로 나누기

## 로컬 실행

```bash
pip install -r requirements.txt
streamlit run app.py
```

poppler 설치 필요:
- macOS: `brew install poppler`
- Ubuntu: `apt-get install poppler-utils`
- Windows: [poppler releases](https://github.com/osber/poppler-windows/releases) 에서 다운로드 후 PATH 추가
