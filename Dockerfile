FROM pcornetqf/qf-python-base:latest

RUN mkdir /app

COPY qf-query-package /app/qf-query-package

WORKDIR /app/qf-query-package

CMD ["python3", "code/query.py"]