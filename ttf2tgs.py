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

    unicode_value = ord(character)  # 获取字符的 Unicode 码点
    glyph_name = font.getBestCmap().get(unicode_value)  # 从字符映射表中获取 glyph 名称

    if glyph_name:
        glyph = glyph_set[glyph_name]

        bpen = BoundsPen(glyph)
        glyph.draw(bpen)

        bounds = bpen.bounds

        xMin, yMin, xMax, yMax = bounds
        width = xMax - xMin
        height = yMax - yMin

        max_length = max(width, height)

        # Center the glyph in the output image
        dxOffset = 0
        dyOffset = 0

        if width > height:
            dyOffset = (max_length - height) / 2
        else:
            dxOffset = (max_length - width) / 2

        transform = Transform(1, 0, 0, -1, -xMin + dxOffset, height + yMin + dyOffset)

        if scale != 1.0:
            transform = Transform(  # Affine Transform Matrix
                scale,  # xx
                0,  # xy
                0,  # yx
                -scale,  # yy
                -xMin * scale + (1 - scale) * 0.5 * width + dxOffset,  # dx
                (height + yMin) * scale + (1 - scale) * 0.5 * height + dyOffset,  # dy
            )

        spen = SVGPathPen(glyph)
        tpen = TransformPen(spen, transform)
        glyph.draw(tpen)

        svg_root = Element(
            "svg",
            width=str(max_length),
            height=str(max_length),
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
        str = str.strip().replace(" ", "")
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
