FROM python:3.11-slim

ENV TZ=Asia/Jakarta
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

WORKDIR /app

COPY . /app

RUN python -m venv .venv && \
    ./.venv/bin/pip install --upgrade pip && \
    ./.venv/bin/pip install --no-cache-dir -r requirements.txt && \
    ./.venv/bin/pip install playwright && \
    ./.venv/bin/playwright install --with-deps

ENV PATH="/app/.venv/bin:$PATH"

ENTRYPOINT ["python", "main.py", "--headless"]