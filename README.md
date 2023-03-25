# Setup

```shell
python3.9 -m venv env
pip install -r requirements.txt
```

# Usage

```shell
. env/bin/activate
cat urls.txt | env/bin/python phone_numbers_parser.py
```

# Notes

Чтобы проверить свой список урлов, необходимо через перенос строки указать ссылки на страницы в файле urls.txt

Не стал убивать много времени на регулярки, поэтому попадаются лишние значения номеров
