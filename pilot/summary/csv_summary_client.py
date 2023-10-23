import json
import uuid
import logging

from pilot.common.schema import DBType
from pilot.component import SystemApp
from pilot.configs.config import Config
from pilot.configs.model_config import (
    KNOWLEDGE_UPLOAD_ROOT_PATH,
    EMBEDDING_MODEL_CONFIG,
)

from pilot.scene.base import ChatScene
from pilot.scene.base_chat import BaseChat
from pilot.scene.chat_factory import ChatFactory
from pilot.summary.rdbms_db_summary import RdbmsSummary

logger = logging.getLogger(__name__)

CFG = Config()
chat_factory = ChatFactory()


class DBSummaryClient:
    """DB Summary client, provide db_summary_embedding(put db profile and table profile summary into vector store)
    , get_similar_tables method(get user query related tables info)
    Args:
        system_app (SystemApp): Main System Application class that manages the lifecycle and registration of components..
    """

    def __init__(self, system_app: SystemApp):
        self.system_app = system_app

    def db_summary_embedding(self, dbname, db_type):
        """put db profile and table profile summary into vector store"""
        from pilot.embedding_engine.string_embedding import StringEmbedding
        from pilot.embedding_engine.embedding_factory import EmbeddingFactory

        db_summary_client = RdbmsSummary(dbname, db_type)
        embedding_factory = self.system_app.get_component(
            "embedding_factory", EmbeddingFactory
        )
        embeddings = embedding_factory.create(
            model_name=EMBEDDING_MODEL_CONFIG[CFG.EMBEDDING_MODEL]
        )
        vector_store_config = {
            "vector_store_name": dbname + "_summary",
            "vector_store_type": CFG.VECTOR_STORE_TYPE,
            "embeddings": embeddings,
        }
        embedding = StringEmbedding(
            file_path=db_summary_client.get_summary(),
            vector_store_config=vector_store_config,
        )

        for vector_table_info in db_summary_client.get_summary():
            embedding = StringEmbedding(
                vector_table_info,# all_comments
                vector_store_config,
            )
            embedding.source_embedding()

        logger.info("db summary embedding success")

    def get_db_summary(self, dbname, query, topk):
        from pilot.embedding_engine.embedding_engine import EmbeddingEngine
        from pilot.embedding_engine.embedding_factory import EmbeddingFactory

        vector_store_config = {
            "vector_store_name": dbname + "_profile",
            "vector_store_type": CFG.VECTOR_STORE_TYPE,
        }
        embedding_factory = CFG.SYSTEM_APP.get_component(
            "embedding_factory", EmbeddingFactory
        )
        knowledge_embedding_client = EmbeddingEngine(
            model_name=EMBEDDING_MODEL_CONFIG[CFG.EMBEDDING_MODEL],
            vector_store_config=vector_store_config,
            embedding_factory=embedding_factory,
        )
        table_docs = knowledge_embedding_client.similar_search(query, topk)
        ans = [d.page_content for d in table_docs]
        return ans

    def init_db_summary(self):
        db_mange = CFG.LOCAL_DB_MANAGE
        dbs = db_mange.get_db_list()
        for item in dbs:
            try:
                self.db_summary_embedding(item["db_name"], item["db_type"])
            except Exception as e:
                logger.warn(
                    f'{item["db_name"]}, {item["db_type"]} summary error!{str(e)}', e
                )