import os
from enum import Enum

from common.config import PROJECT_NAME


def set_working_dir():
    if not os.getcwd().endswith(PROJECT_NAME):
        pre_path, _ = os.getcwd().split(PROJECT_NAME)
        cwd_path = pre_path + PROJECT_NAME
        os.chdir(cwd_path)
    return os.getcwd()


class Status(Enum):
    NotFound = "查询不到"
    InfoReceived = "收到信息"
    InTransit = "运输途中"
    Expired = "运输过久"
    AvailableForPickup = "到达待取"
    OutForDelivery = "派送途中"
    DeliveryFailure = "投递失败"
    Delivered = "成功签收"
    Exception = "可能异常"

class SubStatus(Enum):
    NotFound_Other = "运输商没有返回信息."
    NotFound_InvalidCode = "物流单号无效，无法进行查询."

    InfoReceived = "收到信息，暂无细分含义与主状态一致."
    InTransit_PickedUp = "已揽收，运输商已从发件人处取回包裹."
    InTransit_Other = "其它情况，暂无细分除当前已知子状态之外的情况."
    InTransit_Departure = "已离港，货物离开起运地（国家/地区）港口."
    InTransit_Arrival = "已到港，货物到达目的地（国家/地区）港口."
    InTransit_CustomsProcessing = "清关中，货物在海关办理进入或出口的相关流程中."
    InTransit_CustomsReleased = "清关完成，货物在海关完成了进入或出口的流程."
    InTransit_CustomsRequiringInformation = "需要资料，在清关中流程中承运人需要提供相关资料才能完成清关."

    Expired_Other = "运输过久，暂无细分含义与主状态一致."

    AvailableForPickup_Other = "到达待取，暂无细分含义与主状态一致."

    OutForDelivery_Other = "派送途中，暂无细分含义与主状态一致."

    DeliveryFailure_Other = "其它情况，暂无细分除当前已知子状态之外的情况."
    DeliveryFailure_NoBody = "找不到收件人，派送中的包裹暂时无法联系上收件人，导致投递失败."
    DeliveryFailure_Security = "安全原因，派送中发现的包裹安全、清关、费用问题，导致投递失败."
    DeliveryFailure_Rejected = "拒收，收件人因某些原因拒绝接收包裹，导致投递失败."
    DeliveryFailure_InvalidAddress = "地址错误，由于收件人地址不正确，导致投递失败."

    Delivered_Other = "成功签收，暂无细分含义与主状态一致."
    Exception_Other = "其它情况，暂无细分除当前已知子状态之外的情况."
    Exception_Returning = "退件中，包裹正在送回寄件人的途中."
    Exception_Returned = "退件签收，寄件人已成功收到退件."
    Exception_NoBody = "找不到收件人，在派送之前发现的收件人信息异常."
    Exception_Security = "安全原因，在派送之前发现异常，包含安全、清关、费用问题."
    Exception_Damage = "损坏，在承运过程中发现货物损坏了."
    Exception_Rejected = "拒收，在派送之前接收到有收件人拒收情况."
    Exception_Delayed = "延误，因各种情况导致的可能超出原定的运输周期."
    Exception_Lost = "丢失，因各种情况导致的货物丢失."
    Exception_Destroyed = "销毁，因各种情况无法完成交付的货物并进行销毁."
    Exception_Cancel = "取消，因为各种情况物流订单被取消了."


if __name__ == '__main__':
    print(set_working_dir())
