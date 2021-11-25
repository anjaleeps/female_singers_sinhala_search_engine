import io
import json
from elasticsearch import Elasticsearch, helpers
from elastic_config import Config

elasticsearch = Elasticsearch([{'host': Config.host.value, 'port': Config.port.value}])


def index_data():
    file = io.open('./data_processed.json', mode="r", encoding="utf-8")
    singersData = json.loads(file.read())
    helpers.bulk(elasticsearch, singersData, index=Config.index.value)


if __name__ == "__main__":
    index_data()
