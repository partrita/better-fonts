    # 파이썬 공식 이미지를 기반으로 합니다.
    FROM python:3.9-slim-buster

    # 작업 디렉토리를 /app으로 설정합니다.
    WORKDIR /app

    # requirements.txt를 먼저 복사하여 종속성 설치를 캐싱합니다.
    COPY requirements.txt .
    RUN pip install --no-cache-dir -r requirements.txt

    # 폰트 디렉토리를 /app/fonts로 복사합니다.
    COPY fonts/ ./fonts/

    # src 디렉토리 전체를 /app/src로 복사합니다.
    # 이렇게 하면 컨테이너 내부의 경로가 로컬과 동일하게 src/better_fonts/app.py가 됩니다.
    COPY src/ ./src/

    # 애플리케이션을 실행합니다.
    # WORKDIR이 /app이므로, /app/src/better_fonts/app.py 경로가 됩니다.
    CMD ["python", "src/better_fonts/app.py"]