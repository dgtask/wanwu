from utils.config_util import es
from elasticsearch import helpers
from utils.es_util import check_index_exists
from log.logger import logger

from settings import DELETE_BACTH_SIZE
from utils.util import validate_index_name

def delete_data_by_qa_info(index_name: str, qa_name: str, qa_id: str):
    """根据索引名和 qa_name, qa_id字段 精确匹配删除文档，并返回删除操作的状态"""
    # 构建查询条件
    query = {
        "query": {
            "bool": {
                "must": [
                    {"term": {"QABase": qa_name}},
                    {"term": {"QAId": qa_id}},
                ]
            }
        }
    }
    try:
        deleted_num = 0
        # 使用 scan API 获取匹配的文档 ID
        scan_kwargs = {
            "index": index_name,
            "query": query,
            "scroll": "1m",
            "size": 100  # 每次返回的文档数量
        }
        if check_index_exists(index_name): #兼容老知识库没有file_control_xxx索引
            delete_actions = []
            for doc in helpers.scan(es, **scan_kwargs):
                delete_actions.append({
                    "_op_type": "delete",
                    "_index": index_name,
                    "_id": doc['_id']
                })
                if len(delete_actions) >= DELETE_BACTH_SIZE:
                    logger.info(f"索引 '{index_name}' qa_name:{qa_name} , 删除文档数量: {deleted_num}")
                    # 使用 bulk API 批量删除
                    res = helpers.bulk(es, delete_actions)
                    deleted_num += res[0]
                    delete_actions = []  # 清空 delete_actions
            if len(delete_actions) > 0:
                logger.info(f"索引 '{index_name}' qa_name:{qa_name} , 删除文档数量: {deleted_num}")
                # 最后的残留 bulk API 也批量删除
                res = helpers.bulk(es, delete_actions)
                deleted_num += res[0]
            es.indices.refresh(index=index_name)
        delete_status = {
            "success": True,
            "deleted": deleted_num
        }
    except Exception as e:
        delete_status = {
            "success": False,
            "error": str(e),
        }

    return delete_status


def bulk_add_index_data(index_name, qa_base_name, data):
    """使用 helpers.bulk() 批量上传数据到指定的 Elasticsearch 索引，并返回操作状态"""
    actions = []
    # 首先校验index命名是否合法
    is_index_valid, reason = validate_index_name(index_name)  # 创建普通文本类型索引
    if not is_index_valid:
        print("index invalid")
        return {"success": False, "uploaded": len(data), "error": reason}

    for item in data:
        doc_id = item['qa_pair_id']
        action = {
            "_op_type": "index",
            "_index": index_name,
            "_id": doc_id,
            "_source": item
        }
        actions.append(action)
    # 执行批量操作
    try:
        helpers.bulk(es, actions)
        # es.indices.refresh(index=index_name)
        logger.info(
            f"bulk_add_index_data, index_name:'{index_name}', qa_base_name:'{qa_base_name}' 添加成功。文档数量: {len(actions)}")
        return {"success": True, "uploaded": len(actions), "error": None}
    except Exception as e:
        # 专门处理批量索引错误
        error_count = len(e.errors)
        logger.error(f"批量索引失败！共 {error_count}/{len(actions)} 个文档索引失败")
        # 打印每个失败文档的详细原因
        for i, error in enumerate(e.errors[:5]):  # 最多打印前5个错误
            doc_id = error['index'].get('_id', '未指定ID')
            reason = error['index']['error']['reason']
            error_type = error['index']['error']['type']
            logger.error(f"失败文档 #{i + 1} - ID: {doc_id}")
            logger.error(f"    → 错误类型: {error_type}")
            logger.error(f"    → 原因: {reason}")
        if error_count > 5:
            logger.error(f"...... 另有 {error_count - 5} 个错误未显示 ......")

        # 如果批量操作失败，返回失败状态和错误信息
        logger.info(f"bulk_add_index_data have err, index_name:'{index_name}',qa_base_name:{qa_base_name}, item:{item}")
        import traceback
        logger.error(traceback.format_exc())
        return {"success": False, "uploaded": len(actions), "error": str(e)}


def delete_qa_ids(index_name, qa_base_name, qa_base_id, qa_pair_ids):
    """ delete_qa_ids """
    query = {
        "query": {
            "bool": {
                "must": [
                    {"term": {"QABase": qa_base_name}},
                    {"term": {"QAId": qa_base_id}},
                    {"terms": {"qa_pair_id": qa_pair_ids}},
                ]
            }
        }
    }

    try:
        deleted_num = 0
        scan_kwargs = {
            "index": index_name,
            "query": query,
            "scroll": "1m",
            "size": 100  # 每次返回的文档数量
        }

        delete_actions = []
        for doc in helpers.scan(es, **scan_kwargs):
            delete_actions.append({
                "_op_type": "delete",
                "_index": index_name,
                "_id": doc['_id']
            })
            if len(delete_actions) >= DELETE_BACTH_SIZE:
                logger.info(f"索引 '{index_name}' qa_base_name:{qa_base_name} , 删除文档数量: {deleted_num}")
                # 使用 bulk API 批量删除
                res = helpers.bulk(es, delete_actions)
                deleted_num += res[0]
                delete_actions = []  # 清空 delete_actions
        if len(delete_actions) > 0:
            logger.info(f"索引 '{index_name}' qa_base_name:{qa_base_name} , 删除文档数量: {deleted_num}")
            # 最后的残留 bulk API 也批量删除
            res = helpers.bulk(es, delete_actions)
            deleted_num += res[0]
        es.indices.refresh(index=index_name)
        delete_status = {
            "success": True,
            "deleted": deleted_num
        }
    except Exception as e:
        delete_status = {
            "success": False,
            "error": str(e),
        }

    return delete_status


def update_qa_data(index_name, qa_base_name, qa_pair_id, upsert_data):
    """ update_qa_status"""

    actions = [{
        "_op_type": "update",
        "_index": index_name,
        "_id": qa_pair_id,
        "doc": upsert_data
    }]

    # 执行批量操作
    try:
        helpers.bulk(es, actions)
        es.indices.refresh(index=index_name)
        logger.info(f"索引 '{index_name}' qa_base_name:{qa_base_name} , 更新成功: {upsert_data}")
        return {"success": True, "upserted": len(actions), "error": None}
    except Exception as e:
        # 如果批量操作失败，返回失败状态和错误信息
        return {"success": False, "upserted": len(actions), "error": str(e)}