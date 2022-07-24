# 生成点阵字体文件
import numpy as np
from PIL import ImageFont, ImageDraw, Image

# 字体偏移， 不同字体生成可能会有偏移
OFFSET = (0, 0)
# 生成字体数量，3000个约占 120k 空间, 10k 内存
FONT_NUM = 7000
FONT_SIZE = 16  # 其他字号可能有些问题
FONT_FILE = "unifont-14.0.04.ttf"
CHAR_SET_FILE = "text.txt"

WORDS = list(open(CHAR_SET_FILE, encoding="utf-8").read())
if len(list(set(WORDS))) != len(WORDS):
    print("字符集有重复字")
if len(WORDS) < FONT_NUM:
    FONT_NUM = len(WORDS)
# WORDS.sort()
# open("7000.txt", "w", encoding="utf-8").write("".join(WORDS))
# print(WORDS)
FONT = ImageFont.truetype(font=FONT_FILE, size=FONT_SIZE)

# 生成的 bmf
bitmap_fonts = open(FONT_FILE.split('.')[0] + "-" + str(FONT_NUM) + ".v2.bmf", "wb")


def get_im(word, width, height, offset: tuple = OFFSET):
    im = Image.new('1', (width, height), (1,))
    draw = ImageDraw.Draw(im)
    draw.text(offset, word, font=FONT)
    return im


def to_bitmap(word):
    code = 0x00
    data_code = word.encode("utf-8")
    width = FONT_SIZE
    # fixme: 如果英文为 8 宽度无法存储
    # if ord(word) < 128:
    #     width = 8
    # else:
    #     width = 16
    try:
        for byte in range(len(data_code)):
            code |= data_code[byte] << (len(data_code) - byte - 1) * 8
    except IndexError:
        print(word, word.encode("utf-8"))

    bp = (~np.asarray(get_im(word, width=width, height=FONT_SIZE))).astype(np.int32)

    bmf = []

    for line in bp.reshape((-1, 8)):
        v = 0x00
        for _ in line:
            v = (v << 1) + _
        bmf.append(v)
    # print(bp)
    # for b in bp:
    #     v = 0
    #     for _ in b[0:8]:
    #         v = (v << 1) + _
    #     bmf.append(v)
    # #
    # for e in bp:
    #     v = 0
    #     for _ in e[8:]:
    #         v = (v << 1) + _
    #     bmf.append(v)

    bitmap_fonts.write(bytearray(bmf))


# 字节记录占位
bitmap_fonts.write(bytearray([
    66, 77,  # 标记
    2,  # 版本
    0,  # 映射方式
    0, 0, 0,  # 位图开始字节
    FONT_SIZE,  # 字号
    0, 0, 0, 0, 0, 0, 0, 0  # 兼容项
]))

for _ in range(FONT_NUM):
    bitmap_fonts.write(bytearray(WORDS[_].encode("utf-8")))
print(f"正在生成文件", FONT_FILE.split('.')[0] + "-" + str(FONT_NUM) + ".v2.bmf :")
print("\t索引写入完毕，起始字节位：", hex(bitmap_fonts.tell()), "预计载入字体RAM占用:", f'{bitmap_fonts.tell() / 1024:.2f}kB')
start_bitmap = bitmap_fonts.tell()

# 点阵开始字节写入
bitmap_fonts.seek(0x04, 0)
bitmap_fonts.write(bytearray([start_bitmap >> 16, (start_bitmap & 0xff00) >> 8, start_bitmap & 0xff]))
bitmap_fonts.seek(start_bitmap, 0)
# 开始写入点阵
for _ in range(FONT_NUM):
    to_bitmap(WORDS[_])

print("\t点阵写入完毕，总大小：", f'{bitmap_fonts.tell() / 1024:.2f}kB', "总字数：", FONT_NUM, "字")
print(f"生成完毕")
bitmap_fonts.close()
