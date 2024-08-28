import time

import pandas as pd

from api.logistic import LogisticApi
from common.config import CSV_FILE_PATH
from common.exts import logger
from common.util import Status, SubStatus, set_working_dir


def parse_csv_file(csv_file_path: str = CSV_FILE_PATH):
    set_working_dir()
    # 读取 CSV 文件
    df = pd.read_csv(csv_file_path)

    # 获取快递列的数据
    parsed_data = dict()
    express_data = df['快递'].to_dict()
    for index, express_no in express_data.items():
        parsed_data.update({
            express_no: {
                "express_index": index,
                "express_status": "",
                "express_days": ""}

        })
    logger.info(parsed_data)
    # 打印特定列的数据
    return parsed_data


def register_logistic_no(csv_file_path: str = CSV_FILE_PATH):
    csv_data = parse_csv_file(csv_file_path)

    # 将 csv_data.keys() 分批，每批最多 40 个
    batch_size = 40
    batches = [list(csv_data.keys())[i:i + batch_size] for i in range(0, len(csv_data), batch_size)]

    accepted_logistic_nos, rejected_logistic_info = [], []

    for batch in batches:
        time.sleep(0.5)
        register_data = [{"number": express_no} for express_no in batch]
        logger.info(f"注册批次，包含 {len(register_data)} 个物流单号")
        res = LogisticApi.register_logistic_no(register_data).execute().json()

        # 获取注册成功物流信息
        for accepted_data in res["data"]["accepted"]:
            for data in accepted_data:
                accepted_logistic_nos.append(data.get("number"))

        # 获取注册失败物流信息
        for rejected_data in res["data"]["rejected"]:
            for data in rejected_data:
                rejected_logistic_info.append({
                    "rejected_logistic_no": data.get("number"),
                    "rejected_message": data.get("error").get("message")
                })

    logger.info(f"注册成功物流号:{accepted_logistic_nos}, 注册失败物流号及其失败原因: {rejected_logistic_info}")
    logger.info(f"共处理 {len(batches)}个批次")
    return accepted_logistic_nos, rejected_logistic_info


def get_remain_quota():
    res = LogisticApi.get_remain_quota().execute()
    if res.status_code == 0:
        res = res.json()
        logger.info(f"当前已经使用的单量:{res['data']['quota_used']},当前剩余的可用单量:{res['data']['quota_remain']}")
    else:
        logger.error(f"查询剩余可用单量异常! 状态码为:{res.status_code}")


def query_logistic_detail():
    accepted_logistic_nos, _ = register_logistic_no()
    # 将 accepted_logistic_nos 分批，每批最多 40 个
    batch_size = 40
    batches = [accepted_logistic_nos[i:i + batch_size] for i in range(0, len(accepted_logistic_nos), batch_size)]

    logger.info(f"查询物流信息ing, 此次查询物流单号为:{batches}")
    all_results = []
    accepted_logistic_nos, rejected_logistic_info = [], []

    for batch in batches:
        payload = [{"number": number} for number in batch]
        logger.info(f"处理批次，包含 {len(payload)} 个物流单号")
        res = LogisticApi.query_logistic_detail(payload).execute().json()
        all_results.append(res)
        # 获取查询成功物流信息
        for accepted_data in res["data"]["accepted"]:
            for data in accepted_data:
                # todo 字段获取待确定
                # accepted_logistic_nos.append(data.get("number"))
                status = data.get("latest_status").get("status")
                sub_status = data.get("latest_status").get("sub_status")
                # 获取枚举值
                status_value = Status[status].value if status in Status.__members__ else status
                sub_status_value = SubStatus[sub_status].value if sub_status in SubStatus.__members__ else sub_status
                
                express_status = f"{status_value} - {sub_status_value}"
                logger.info(f"物流状态: {express_status}")

        # 获取查询失败物流信息
        for rejected_data in res["data"]["rejected"]:
            for data in rejected_data:
                rejected_logistic_info.append({
                    "rejected_logistic_no": data.get("number"),
                    "rejected_message": data.get("error").get("message")
                })

    logger.info(f"共处理 {len(batches)} 批次")
    logger.info(all_results)
    return all_results


if __name__ == '__main__':
    LogisticApi.register_logistic_no([{"number": "1ZF203H80313920646"}]).execute().json()
    LogisticApi.query_logistic_detail(
        [
            {
                "number": "1ZF203H80313920646"
            }
        ]
    ).execute().json()
