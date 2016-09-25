# Kindle

## Install dependencies

```shell
pip3 install -r requirements.txt
```

## Run

```shell
python3 kindle.py
```

**crontab**

```shell
5 0 * * * /path/to/kindle/cron.sh >> /var/log/kindle.log 2>&1
```