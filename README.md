# ttf2tgs

Export Font Glyphs to Telegram Animated Sticker Format

### Requirements

- Python 3.x

Install pip dependencies

```sh
pip install -r requirements.txt
```

Note: If you use python virtual environments, do not forget to create and activate it before installing dependencies.

### Usage

Assume that you have font file `SomeFonts.ttf` (or OpenType), then input all the characters you want to export in `characters.txt`.

```sh
python3 ttf2tgs.py SomeFonts.ttf characters.txt
```

And you will get Telegram Animated Sticker files under the `tgs` folder.

### Options

```txt

options:
  -h, --help       show this help message and exit
  --output OUTPUT  target directory to the output TGS files, default ./tgs
  --scale SCALE    output image scale factor, between 0 and 1.0
  --svg            save glyph SVG files
```

### Thanks

- [fonttools](https://github.com/fonttools/fonttools) - A library to manipulate font files from Python.
- [python-lottie](https://gitlab.com/mattbas/python-lottie/) - Python framework to manipulate lottie / telegram animated sticker files
