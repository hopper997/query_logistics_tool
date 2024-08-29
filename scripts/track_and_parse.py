import os
import time

import pandas as pd

from api.logistic import LogisticApi
from common.config import PROJECT_NAME
from common.exts import logger
from common.util import Status, SubStatus, set_working_dir, get_csv_file

CSV_FILE_PATH = os.path.join("data", get_csv_file()[0])
CSV_FILE_PATH = os.path.normpath(CSV_FILE_PATH).replace('\\', '/')


def parse_csv_file(csv_file_path: str):
    set_working_dir()
    # 读取 CSV 文件
    df = pd.read_csv(csv_file_path)

    # 获取快递列的数据
    parsed_data = []
    express_data = df['快递'].to_dict()
    for express_no in express_data.values():
        parsed_data.append(express_no)
    logger.info(f"parsed_data:{parsed_data}")
    # 打印特定列的数据
    return parsed_data


def register_logistic_no(csv_file_path: str):
    csv_data = parse_csv_file(csv_file_path)

    # 将 csv_data.keys() 分批，每批最多 40 个
    batch_size = 40
    batches = [csv_data[i:i + batch_size] for i in range(0, len(csv_data), batch_size)]

    accepted_logistic_nos, rejected_logistic_info = [], []

    for batch in batches:
        time.sleep(0.5)
        register_data = [{"number": express_no} for express_no in batch]
        logger.info(f"注册批次，包含 {len(register_data)} 个物流单号")
        res = LogisticApi.register_logistic_no(register_data).execute().json()

        # 获取注册成功物流信息
        for accepted_data in res["data"]["accepted"]:
            accepted_logistic_nos.append(accepted_data.get("number"))

        # 获取注册失败物流信息
        for rejected_data in res["data"]["rejected"]:
            logger.info(f"rejected_data:{rejected_data}")
            express_no = rejected_data.get("number")
            error_code =  rejected_data.get("error").get("code")
            # todo 如果是已被注册的错误 则直接将物流单号添加到accepted_logistic_nos
            if error_code == -18019901:
                accepted_logistic_nos.append(express_no)
            else:
                rejected_logistic_info.append({
                    "rejected_logistic_no": rejected_data.get("number"),
                    "rejected_message": rejected_data.get("error").get("message")
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


def query_logistic_detail(csv_file_path: str):
    accepted_logistic_nos, _ = register_logistic_no(csv_file_path)
    # 将 accepted_logistic_nos 分批，每批最多 40 个
    batch_size = 40
    batches = [accepted_logistic_nos[i:i + batch_size] for i in range(0, len(accepted_logistic_nos), batch_size)]

    logger.info(f"查询物流信息ing, 此次查询物流单号为:{batches}")
    accepted_logistic_info, rejected_logistic_info = [], []
    for batch in batches:
        payload = [{"number": number} for number in batch]
        logger.info(f"处理批次，包含 {len(payload)} 个物流单号")
        res = LogisticApi.query_logistic_detail(payload).execute().json()
        # 获取查询成功物流信息
        for accepted_data in res["data"]["accepted"]:
            logger.info(f"accepted_data:{accepted_data}")
            status = accepted_data.get("track_info", {}).get("latest_status", {}).get("status")
            sub_status = accepted_data.get("track_info", {}).get("latest_status", {}).get("sub_status")
            # 获取枚举值
            status_value = Status[status].value if status in Status.__members__ else status
            sub_status_value = SubStatus[sub_status].value if sub_status in SubStatus.__members__ else sub_status

            express_status = f"{status_value} - {sub_status_value}"
            express_time_iso = accepted_data.get("track_info", {}).get("latest_event", {}).get("time_iso")
            express_no = accepted_data.get("number")
            accepted_logistic_info.append({
                "express_no": express_no,
                "express_status": express_status,
                "express_time_iso": express_time_iso,
            })
        # 获取查询失败物流信息
        for rejected_data in res["data"]["rejected"]:
            rejected_logistic_info.append({
                "express_no": rejected_data.get("number"),
                "express_status": "查询失败",
                "rejected_message": rejected_data.get("error").get("message")
            })

    logger.info(f"共处理 {len(batches)} 批次")
    logger.warning(f"rejected_logistic_info:{rejected_logistic_info}")
    return accepted_logistic_info, rejected_logistic_info


def write_logistic_detail_to_csv(csv_file_path: str = CSV_FILE_PATH):
    logger.info(f"csv_file_path:{csv_file_path}")
    accepted_logistic_info, rejected_logistic_info = query_logistic_detail(csv_file_path)
    # 读取原始 CSV 文件
    df = pd.read_csv(csv_file_path)
    # 处理 accepted_logistic_info
    for info in accepted_logistic_info:
        logistic_no = info.get('express_no')
        express_status = info.get('express_status')
        express_time_iso = info.get('express_time_iso')
        # 更新 DataFrame
        df.loc[df['快递'] == logistic_no, '物流状态'] = express_status
        df.loc[df['快递'] == logistic_no, '物流时间'] = express_time_iso

    # 处理 rejected_logistic_info
    for info in rejected_logistic_info:
        logistic_no = info.get('rejected_logistic_no')
        express_status = info.get("express_status")
        rejected_message = info.get('rejected_message')
        # 更新 DataFrame
        df.loc[df['快递'] == logistic_no, '失败原因'] = rejected_message
        df.loc[df['快递'] == logistic_no, '物流状态'] = express_status

    # 保存更新后的 CSV 文件
    df.to_csv(csv_file_path, index=False)
    logger.info(f"已更新 CSV 文件: {csv_file_path}")
