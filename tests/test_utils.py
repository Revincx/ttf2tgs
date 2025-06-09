import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import ttf2tgs


def test_gen_char_name_simple():
    assert ttf2tgs.gen_char_name('A') == 'A_65'


def test_gen_char_name_escape():
    assert ttf2tgs.gen_char_name('/') == 'slash_47'
    assert ttf2tgs.gen_char_name('<') == 'lt_60'


def test_get_char_array_deduplicate(tmp_path):
    chars_file = tmp_path / "chars.txt"
    chars_file.write_text("AABBC")
    assert ttf2tgs.get_char_array(str(chars_file)) == list("ABC")
