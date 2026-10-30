FROM python:3.14-slim

WORKDIR /app

COPY inf1103-labs-smart-auditor.py .

CMD ["python", "inf1103-labs-smart-auditor.py"]