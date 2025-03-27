import os,sys

from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.misc.transform import Transform
from fontTools.pens.boundsPen import BoundsPen
from xml.etree.ElementTree import Element, tostring
from lottie.importers.svg import import_svg
from lottie.exporters.core import export_tgs
from argparse import ArgumentParser

output_path = "./tgs"
scale = 1.0

def export_glyph(font: TTFont, character: str):
    glyph_set = font.getGlyphSet()
    
    # 获取字体的em方格大小（设计单位）
    units_per_em = font['head'].unitsPerEm
    
    unicode_value = ord(character)
    glyph_name = font.getBestCmap().get(unicode_value)

    if glyph_name:
        glyph = glyph_set[glyph_name]

        # 检查字形是否有轮廓
        bpen = BoundsPen(glyph_set)
        glyph.draw(bpen)
        
        if bpen.bounds is None:
            print(f"Character '{character}' has no outline, skipping.")
            return
            
        # 使用em方格作为SVG大小
        svg_size = units_per_em
        
        # 获取字形的边界
        xMin, yMin, xMax, yMax = bpen.bounds
        
        # 计算边界中心
        center_x = (xMin + xMax) / 2
        center_y = (yMin + yMax) / 2
        
        # 根据翻转与缩放修正变换矩阵
        if scale == 1.0:
            transform = Transform(
                1, 0,
                0, -1,
                (svg_size / 2) - center_x,
                (svg_size / 2) + center_y
            )
        else:
            transform = Transform(
                scale, 0,
                0, -scale,
                (svg_size / 2) - scale * center_x,
                (svg_size / 2) + scale * center_y
            )

        spen = SVGPathPen(glyph)
        tpen = TransformPen(spen, transform)
        glyph.draw(tpen)

        svg_root = Element(
            "svg",
            width=str(svg_size),
            height=str(svg_size),
            xmlns="http://www.w3.org/2000/svg",
        )
        svg_root.append(
            Element("path", d=spen.getCommands(), fill="black", stroke="none")
        )

        with open(f"{output_path}/{gen_char_name(character)}.svg", "wb") as f:
            f.write(tostring(svg_root))
    else:
        print(f"No glyph found for the character {character}")
        


def get_char_array(file_path: str):
    with open(file_path, "r") as f:
        str = f.read()
        str = str.strip().replace(" ", "").replace("\n", "").replace("\r", "")
        # remove duplicate characters
        str = "".join(dict.fromkeys(str))
        return list(str)
    
def gen_char_name(char: str):
    # escape special characters
    charname = char
    if char == "\\":
        charname = "backslash"
    elif char == "/":
        charname = "slash"
    elif char == ":":
        charname = "colon"
    elif char == "*":
        charname = "star"
    elif char == "?":
        charname = "question"
    elif char == "\"":
        charname = "quote"
    elif char == "<":
        charname = "lt"
    elif char == ">":
        charname = "gt"
    elif char == "|":
        charname = "pipe"
    return f"{charname}_{ord(char)}"

class MyParser(ArgumentParser):
    def error(self, message):
        sys.stderr.write('error: %s\n' % message)
        self.print_help()
        sys.exit(2)

if __name__ == "__main__":
    parser = MyParser(
        description="Convert a TTF font to a Lottie-compatible JSON file"
    )
    parser.add_argument("font", type=str, help="Path to the TTF/OTF font file")
    parser.add_argument(
        "chars", type=str, help="Path to the file containing the characters to convert"
    )

    parser.add_argument("--output", type=str, help="Target directory to the output TGS files")
    parser.add_argument(
        "--scale",
        type=float,
        help="Output image scale factor, less than 1.0",
        default=1.0,
    )
    parser.add_argument("--svg", action="store_true", help="Save SVG files")

    args = parser.parse_args()

    output_path = args.output if args.output else output_path
    scale = args.scale if args.scale < 1 and args.scale > 0 else scale

    try:
        font = TTFont(args.font)
    except Exception as e:
        print(f"Incorrect font file: {e}")
        exit()

    chars = get_char_array(args.chars)

    # mkdir output
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    for char in chars:
        export_glyph(font, char)
        svg = import_svg(f"{output_path}/{gen_char_name(char)}.svg")
        tgs = export_tgs(svg, f"{output_path}/{gen_char_name(char)}.tgs", True, True)

        if args.svg is False:
            os.remove(f"{output_path}/{gen_char_name(char)}.svg")

        print(f"Exported character '{char}' to {output_path}/{gen_char_name(char)}.tgs")
