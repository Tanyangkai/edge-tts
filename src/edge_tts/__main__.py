"""
__main__ for edge_tts.
"""

"""
这是 edge_tts 的 __main__ 模块。

从 util 模块中导入了 main 函数，然后检查当前脚本是否作为主程序运行（而不是作为模块导入到其他程序中）。
如果是主程序运行，那么执行 main() 函数，这可以用于启动 edge_tts 的相关功能。

这个结构允许你在命令行中执行模块时运行一些代码，但如果你将这个模块作为一个库导入到其他程序中，它将不会执行 main() 函数。
"""

from .util import main

if __name__ == "__main__":
    main()
