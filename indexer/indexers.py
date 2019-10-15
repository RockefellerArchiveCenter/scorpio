import json
import shortuuid

from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search

from scorpio import config


class Indexer:

    def __init__(self):
        self.client = Elasticsearch([config.ELASTICSEARCH['host']])

    def generate_id(self):
        return shortuuid.uuid()

    def add(self, data):
        if isinstance(data, str):
            data = json.loads(data)
        identifier = [i['identifier'] for i in data['external_identifiers'] if i['source'] == 'archivesspace'][0]
        s = Search(using=self.client).query('match_phrase', external_identifiers__identifier=identifier)
        response = s.execute()
        if response.hits.total == 1:
            es_id = response[0].meta.id
        else:
            es_id = self.generate_id()
        # TODO: better type handling
        # TODO: handle cases where there is more than one hit
        return self.client.index(index=data.get('$').lstrip('transformer.resources.').lower(),
                                 doc_type='_doc', id=es_id, body=data, refresh=True)

    def delete(self, data):
        if isinstance(data, str):
            data = json.loads(data)
        identifier = [i['identifier'] for i in data['external_identifiers'] if i['source'] == 'archivesspace'][0]
        # TODO: better type handling
        s = Search(using=self.client, index=data.get('$').lstrip('transformer.resources.').lower()).query('match_phrase', external_identifiers__identifier=identifier)
        response = s.delete()
        return response