import os
import re
from copy import copy
from typing import ClassVar

from openai import Embedding
import vecs

from models import Job

# number of related job descriptions to return
QUERY_MAX: int = 7


def _setup_vector_store() -> vecs.Collection:
    _host = os.environ.get('RAW_SUPABASE_URL')
    _user = os.environ.get('RAW_SUPABASE_USER')
    _password = os.environ.get('PG_PASS')
    _port = 5432
    _db_name = 'postgres'
    _url = f"postgresql://{_user}:{_password}@{_host}:{_port}/{_db_name}"
    vx = vecs.create_client(_url)
    return vx.get_or_create_collection(name="collection_test_1", dimension=1536)


class EmbeddingManager:
    _collection: ClassVar[vecs.Collection] = _setup_vector_store()

    @staticmethod
    def _preprocess_description(desc: str) -> str:
        """ Preprocess job description before generating embeddings. """
        _desc = copy(desc)
        _desc = _desc.lower()

        # remove all 'click to apply' links
        pattern = r'\[click to apply\]\((.*?)\)'
        _desc = re.sub(pattern, '', _desc)

        # remove unnecessary lines
        lines = desc.split('\n')
        keywords = ["**posted on**", "**hourly range**", "**country**", "**location requirement**"]
        filtered_lines = [line for line in lines if not any(keyword in line for keyword in keywords)]
        _desc = '\n'.join(filtered_lines)

        return _desc

    @classmethod
    def generate_embeddings(cls, data: list[dict]):
        """ Generate embeddings for a batch of job descriptions.

        This should only need to be executed once to bootstrap the vector store.
        """
        embeddings = []

        for row in data:
            embed = cls._embed(row['desc'])
            embeddings.append((row['id'],
                               embed,
                               {}))

        cls._collection.upsert(records=embeddings)

    @classmethod
    def query(cls, text: str) -> list[str]:
        """ Get a list of related UUID's for rows related to given job description. """
        # TODO: use an adapter to convert str values to UUID4
        embedding = cls._embed(text)

        # TODO: add embeddings to vector store
        return cls._collection.query(
            data=embedding,
            limit=QUERY_MAX,
            include_value=False
        )

    @staticmethod
    def _embed(text: str) -> list[float]:
        _text = EmbeddingManager._preprocess_description(text)
        response = Embedding.create(
            model="text-embedding-ada-002",
            input=[_text]
        )
        return response["data"][0]["embedding"]

    @classmethod
    async def __call__(cls, jobs: list[Job]):
        print(f"Generating embeddings for {len(jobs)} jobs")
        data = [{'id': job.id, 'desc': job.description} for job in jobs]
        cls.generate_embeddings(data)
        print("Finished generating embeddings")


