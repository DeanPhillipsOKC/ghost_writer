import tempfile
from pathlib import Path

import pytest

import ghost_writer.utils.markdown_utils as md_utils

def test_add_page_break():
    assert md_utils.add_page_break().strip().startswith("<div")
    assert "page-break-after" in md_utils.add_page_break()

def test_image_markdown():
    result = md_utils.image_markdown("foo/bar.png", "The Image")
    assert result.strip() == "![The Image](foo/bar.png)"

def test_header_markdown():
    assert md_utils.header_markdown("Hello", 1).startswith("# Hello")
    assert md_utils.header_markdown("Hello", 3).startswith("### Hello")

def test_code_block_markdown():
    code = "print('hi')"
    block = md_utils.code_block_markdown(code, "python")
    assert block.startswith("```python")
    assert code in block
    assert block.strip().endswith("```")

def test_write_markdown(tmp_path):
    # Prepare file path
    md_file = tmp_path / "my" / "doc.md"
    content = "# Title\nText here\n"
    
    # Should create directories and file
    md_utils.write_markdown(content, str(md_file), mode="w")
    assert md_file.exists()
    with open(md_file) as f:
        assert f.read() == content
        
    # Append content
    md_utils.write_markdown("Another line\n", str(md_file), mode="a")
    with open(md_file) as f:
        lines = f.readlines()
        assert lines[0] == "# Title\n"
        assert lines[-1] == "Another line\n"
        
def test_quote_block_markdown():
    text = (
        "First paragraph of the quote.\n"
        "It continues here.\n\n"
        "Second paragraph follows.\n"
        "It also spans multiple lines."
    )
    author = "Test Author"

    result = md_utils.quote_block_markdown(text, author)

    # Check each paragraph is blockquoted correctly
    assert "> First paragraph of the quote." in result
    assert "> It continues here." in result
    assert "> Second paragraph follows." in result
    assert "> It also spans multiple lines." in result

    # Check author attribution
    assert result.strip().endswith(f"> — *{author}*")

