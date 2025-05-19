from ghost_writer.models import Act, Chapter, Book, Idea, Characters
from ghost_writer.tools.convert_to_pdf_tool import MarkdownToPDFTool
from ghost_writer.tools.transcribe_tool import TranscribeTool
from ghost_writer.tools.illustrator_tool import IllustratorTool
from ghost_writer.utils.markdown_utils import add_page_break, header_markdown, quote_block_markdown
from ghost_writer.services.illustration_writer import IllustrationWriter
from ghost_writer.services.scene_writer import SceneWriter
from ghost_writer.services.writer_templates import  get_chapter_illustration_prompt, get_book_cover_illustration_prompt, get_book_frontispiece_illustration_prompt

from pathlib import Path

class NullIllustrator:
    def run(self, prompt, filename=None, size=None):
        # No operation for null illustrator
        pass

class BookWriterService:
    def __init__(
        self, 
        author_agent,
        transcriber=None, 
        illustrator=None, 
        disable_illustration=False, 
        pdf_tool=None,
        output_path='output'
    ):
        self.author_agent = author_agent
        self.transcriber = transcriber or TranscribeTool()
        self.illustrator = (
            NullIllustrator() if disable_illustration else illustrator or IllustratorTool()
        )
        self.chapter_number = 1
        self.artistic_vision = None
        self.pdf_tool = pdf_tool or MarkdownToPDFTool()
        self.output_path = Path(output_path)
        self.images_path = self.output_path / "images"
        self.book_md_path = self.output_path / "book.md"
        self.book_pdf_path = self.output_path / "book.pdf"
        self.scene_writer = SceneWriter(
            author_agent=self.author_agent,
            transcriber=self.transcriber)
        
        self.output_path.mkdir(parents=True, exist_ok=True)
        self.images_path.mkdir(parents=True, exist_ok=True)
        
        self.illustration_writer = IllustrationWriter(
            illustrator=self.illustrator,
            transcriber=self.transcriber,
            images_path=self.images_path,
            output_path=self.output_path
        )

    def set_artistic_vision(self, vision):
        self.artistic_vision = vision

    def write_book_intro(self, book_info: Book):
        self.__write_book_cover( book_info)
        self.__write_frontispiece(book_info)
        self.__write_epigraph(book_info)
        self.transcriber.run(content=add_page_break())
        self.__write_preface(book_info)
        self.transcriber.run(content=add_page_break())
        self.__write_authors_note(book_info)
        self.transcriber.run(content=add_page_break())
        
    def save_pdf(self):
        self.pdf_tool.run(
            markdown_path=str(self.book_md_path),
            output_pdf_path=str(self.book_pdf_path)
        )

    def write_act(self, act: Act, idea: Idea, characters: Characters):
        act_header = header_markdown(text=f"Act {act.act_number}: {act.act_title}", level=2)
        self.transcriber.run(content=act_header)

        for chapter in act.chapters:
            self.__write_chapter(chapter, act, idea, characters)

    def __write_chapter(self, chapter: Chapter, act: Act, idea: Idea, characters: Characters):
        chapter_header = header_markdown(
            text=f"Chapter {self.chapter_number}: {chapter.chapter_title}", level=3
        )
        self.transcriber.run(content=chapter_header)

        self.illustration_writer.write_illustration(
            prompt=get_chapter_illustration_prompt(
                chapter=chapter,
                artistic_vision=self.artistic_vision
            ),
            size='1024x1024',
            filename=str(f"chapter_{self.chapter_number:02}.png")
        )

        self.chapter_number += 1

        for scene in chapter.scenes:
            self.scene_writer.write_scene(scene, act, chapter, idea, characters)

        self.transcriber.run(content=add_page_break())

    def __write_authors_note(self, book_info: Book):
        authors_note_header_md = header_markdown("Author's Note", level=2)
        self.transcriber.run(content=authors_note_header_md)
        
        authors_note_md = book_info.authors_note
        self.transcriber.run(content=authors_note_md)

    def __write_preface(self, book_info: Book):
        preface_header_md = header_markdown("Preface", level=2)
        self.transcriber.run(content=preface_header_md)
        
        self.transcriber.run(content=f"{book_info.preface}\n\n")

    def __write_epigraph(self, book_info: Book):
        epigraph_md = quote_block_markdown(
            text=book_info.epigraph,
            author=book_info.author,
        )
        self.transcriber.run(content=epigraph_md)

    def __write_frontispiece(self, book_info: Book):
        self.illustration_writer.write_illustration(
            prompt=get_book_frontispiece_illustration_prompt(
                book_info=book_info,
                artistic_vision=self.artistic_vision
            ),
            size='1024x1024',
            filename=str("frontispiece.png")
        )

    def __write_book_cover(self, book_info: Book):
        self.illustration_writer.write_illustration(
            prompt=get_book_cover_illustration_prompt(
                book_info=book_info,
                artistic_vision=self.artistic_vision
            ),
            size='1024x1536',
            filename=str("cover.png")
        )
    
        title_md = header_markdown(text=book_info.title, level=1)
        self.transcriber.run(content=title_md)

