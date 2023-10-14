"""
Main package.
"""

import argparse
import asyncio
import sys
from io import TextIOWrapper
from typing import Any, TextIO, Union

from edge_tts import Communicate, SubMaker, list_voices


async def _print_voices(*, proxy: str) -> None:
    """Print all available voices."""
    voices = await list_voices(proxy=proxy)
    voices = sorted(voices, key=lambda voice: voice["ShortName"])
    for idx, voice in enumerate(voices):
        if idx != 0:
            print()

        for key in voice.keys():
            if key in (
                    "SuggestedCodec",
                    "FriendlyName",
                    "Status",
                    "VoiceTag",
                    "Name",
                    "Locale",
            ):
                continue
            pretty_key_name = key if key != "ShortName" else "Name"
            print(f"{pretty_key_name}: {voice[key]}")


async def _run_tts(args: Any) -> None:
    """Run TTS after parsing arguments from command line."""

    try:
        # 用来检查是否可以直接将TTS输出写入终端的
        '''如果标准输入和标准输出都连接到终端，并且用户没有指定将TTS输出写入媒体文件，就会显示警告信息，提示用户TTS输出将写入终端，并要求用户按回车键继续。
        这是为了确保用户明白TTS输出将显示在终端上，并有机会取消操作。'''
        if sys.stdin.isatty() and sys.stdout.isatty() and not args.write_media:
            print(
                "Warning: TTS output will be written to the terminal. "
                "Use --write-media to write to a file.\n"
                "Press Ctrl+C to cancel the operation. "
                "Press Enter to continue.",
                file=sys.stderr,
            )
            # 用于等待用户的输入
            input()
    except KeyboardInterrupt:
        print("\nOperation canceled.", file=sys.stderr)
        return

    # 执行文本到语音合成操作
    tts: Communicate = Communicate(
        args.text,
        args.voice,
        proxy=args.proxy,
        rate=args.rate,
        volume=args.volume,
        pitch=args.pitch,
    )
    # 创建字幕（subtitles）
    subs: SubMaker = SubMaker()

    # 处理TTS输出和创建字幕
    with open(
            args.write_media, "wb"
    ) if args.write_media else sys.stdout.buffer as audio_file:
        async for chunk in tts.stream():
            if chunk["type"] == "audio":
                audio_file.write(chunk["data"])
            elif chunk["type"] == "WordBoundary":
                subs.create_sub((chunk["offset"], chunk["duration"]), chunk["text"])

    sub_file: Union[TextIOWrapper, TextIO] = (
        open(args.write_subtitles, "w", encoding="utf-8")
        if args.write_subtitles
        else sys.stderr
    )
    with sub_file:
        sub_file.write(subs.generate_subs(args.words_in_cue))


async def amain() -> None:
    """Async main function"""
    # 创建一个命令行解析器，用于解析命令行参数。
    parser = argparse.ArgumentParser(description="Microsoft Edge TTS")
    group = parser.add_mutually_exclusive_group(required=True)

    # 添加命令行参数选项
    group.add_argument("-t", "--text", help="what TTS will say")
    group.add_argument("-f", "--file", help="same as --text but read from file")
    parser.add_argument(
        "-v",
        "--voice",
        help="voice for TTS. Default: en-US-AriaNeural",
        default="en-US-AriaNeural",
    )
    group.add_argument(
        "-l",
        "--list-voices",
        help="lists available voices and exits",
        action="store_true",
    )
    parser.add_argument("--rate", help="set TTS rate. Default +0%%.", default="+0%")
    parser.add_argument("--volume", help="set TTS volume. Default +0%%.", default="+0%")
    parser.add_argument("--pitch", help="set TTS pitch. Default +0Hz.", default="+0Hz")
    parser.add_argument(
        "--words-in-cue",
        help="number of words in a subtitle cue. Default: 10.",
        default=10,
        type=float,
    )
    parser.add_argument(
        "--write-media", help="send media output to file instead of stdout"
    )
    parser.add_argument(
        "--write-subtitles",
        help="send subtitle output to provided file instead of stderr",
    )
    parser.add_argument("--proxy", help="use a proxy for TTS and voice list.")

    # 解析命令行参数
    args = parser.parse_args()

    # 如果用户使用 -l 或 --list-voices 选项，列出可用的语音并退出程序。
    if args.list_voices:
        await _print_voices(proxy=args.proxy)
        sys.exit(0)

    # 如果指定了输入文件 (-f 或 --file)，从文件中读取文本内容，否则使用命令行传递的文本 (-t 或 --text)。
    if args.file is not None:
        # 如果文件路径是标准输入（/dev/stdin），则从标准输入读取文本。
        if args.file == "/dev/stdin":
            args.text = sys.stdin.read()
        else:
            # 否则，从指定文件中读取文本。
            with open(args.file, "r", encoding="utf-8") as file:
                args.text = file.read()

    # 如果文本内容存在，调用 _run_tts 函数运行 TTS。
    if args.text is not None:
        await _run_tts(args)


'''
asyncio 是 Python 中的一个库，用于编写基于事件循环的异步程序。
它允许你编写异步代码以处理并发、并行执行的任务，而无需使用多线程或多进程的复杂性。
asyncio 提供了协程（coroutine）和事件循环（event loop）的支持，使开发者能够轻松处理 I/O 操作、网络通信、定时任务等，而不会阻塞主程序的执行。
'''


def main() -> None:
    """Run the main function using asyncio."""
    # 获取事件循环（event loop），在asyncio中用于管理任务的执行和调度。
    loop = asyncio.get_event_loop_policy().get_event_loop()
    try:
        # 运行 asyncio 主函数 amain()，直到其中的所有异步任务完成。
        loop.run_until_complete(amain())
    finally:
        loop.close()


if __name__ == "__main__":
    main()
