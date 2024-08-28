from common.base_api import HttpRequest


class LogisticApi:
    @staticmethod
    def query_logistic_detail(request_body):
        """获取物流详情接口"""
        return HttpRequest(
            path="/track/v2.2/gettrackinfo",
            method="post",
            json=request_body
        )

    @staticmethod
    def register_logistic_no(request_body):
        """注册物流单号接口"""
        return HttpRequest(
            path="/track/v2.2/register",
            method="post",
            json=request_body
        )

    @staticmethod
    def get_remain_quota():
        """获取当前剩余单量接口"""
        return HttpRequest(
            path="/track/v2.2/getquota",
            method="post"
        )
