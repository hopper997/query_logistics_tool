import logging
import os
import time

import colorlog

# from configs.api_config import MAX_LOG_FILES, LOG_COLORS_CONFIG
MAX_LOG_FILES = 50
LOG_COLORS_CONFIG = {
    'DEBUG': 'green',
    'INFO': 'cyan',
    'WARNING': 'yellow',
    'ERROR': 'red',
    'CRITICAL': 'red',
}


class Logger:
    instance = None

    def __new__(cls, *args, **kwargs):
        if not cls.instance:
            cls.instance = super().__new__(cls)
        return cls.instance

    def __init__(self, name, log_level=logging.DEBUG):
        self.name = name
        self._logger = logging.getLogger(self.name)
        # 如果这个logger还没有handler，那么添加handler
        if not self._logger.handlers:
            self._logger.setLevel(log_level)
            formatter = "%(asctime)s - %(filename)s - %(lineno)d - %(levelname)s - %(message)s"
            self.file_formatter = logging.Formatter(formatter)
            self.stream_formatter = colorlog.ColoredFormatter("%(log_color)s" + formatter, log_colors=LOG_COLORS_CONFIG)
            # 创建屏幕-输出到控制台，设置输出等级
            self.streamHandler = logging.StreamHandler()
            self.streamHandler.setLevel(log_level)
            # 创建log文件，设置输出等级
            PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # 根目录
            file_name = time.strftime('%Y_%m%d', time.localtime()) + '.log'
            # file_name = PROJECT_NAME + '.log'
            # 文件保存在根目录下的log文件夹，如没有该文件夹，直接创建
            self.log_path = os.path.join(PROJECT_ROOT, "log")
            if not os.path.exists(self.log_path):
                os.mkdir(self.log_path)
            self.fileHandler = logging.FileHandler(os.path.join(self.log_path, file_name), 'a', encoding='utf-8')
            print(os.path.join(self.log_path, file_name))
            self.fileHandler.setLevel(log_level)

            # 日志切割 每分钟切割一次日志
            # log_file_path = os.path.join(self.log_path, file_name)
            # self.TRFileHandler = TimedRotatingFileHandler(log_file_path, 'M', 1, MAX_LOG_FILES, 'utf-8')
            # self.TRFileHandler.setLevel(log_level)

            # 用formatter渲染这两个Handler
            self.streamHandler.setFormatter(self.stream_formatter)
            self.fileHandler.setFormatter(self.file_formatter)
            # self.TRFileHandler.setFormatter(self.file_formatter)
            # 将这两个Handler加入logger内
            self._logger.addHandler(self.streamHandler)
            self._logger.addHandler(self.fileHandler)
            # self._logger.addHandler(self.TRFileHandler)
            # 清除多余日志文件
            self._clear_log_file()

    def get_logger(self):
        return self._logger

    def _clear_log_file(self):
        """清除log文件,确保log文件的数据始终在{MAX_LOG_FILES}以内"""
        for _, _, files in os.walk(self.log_path):
            if len(files) > MAX_LOG_FILES:
                files.sort(reverse=True)
                for file in files[MAX_LOG_FILES:]:
                    file_path = os.path.join(self.log_path, file)
                    os.remove(file_path)
