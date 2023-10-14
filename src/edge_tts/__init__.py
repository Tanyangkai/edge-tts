"""
__init__ for edge_tts
"""

# 导入所需的模块和类
from . import exceptions
from .communicate import Communicate
from .list_voices import VoicesManager, list_voices
from .submaker import SubMaker
from .version import __version__

'''
__all__ 列表是 Python 中的一个特殊变量，通常用于定义哪些变量、函数或类是一个模块的公共接口。
这句话的意思是，__all__ 列表中列出的变量、函数或类是其他模块可以直接访问的，它们是模块的公开部分。
'''

# 定义在这个模块中可以导入的所有公共接口
__all__ = [
    "Communicate",
    "SubMaker",
    "VoicesManager",
    "exceptions",
    "list_voices",
]
