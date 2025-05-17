from ghost_writer.models import Act, Chapter, Scene, Book
from ghost_writer.tools.convert_to_pdf_tool import MarkdownToPDFTool
from ghost_writer.tools.transcribe_tool import TranscribeTool
from ghost_writer.tools.illustrator_tool import IllustratorTool
from ghost_writer.utils.markdown_utils import add_page_break, header_markdown, image_markdown

from pathlib import Path

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
        self.illustrator = illustrator or IllustratorTool()
        self.chapter_number = 1
        self.artistic_vision = None
        self.disable_illustration = disable_illustration
        self.pdf_tool = pdf_tool or MarkdownToPDFTool()
        self.output_path = Path(output_path)
        self.images_path = self.output_path / "images"
        self.book_md_path = self.output_path / "book.md"
        self.book_pdf_path = self.output_path / "book.pdf"

        self.output_path.mkdir(parents=True, exist_ok=True)
        self.images_path.mkdir(parents=True, exist_ok=True)

    def set_artistic_vision(self, vision):
        self.artistic_vision = vision

    def write_scene(self, scene: Scene, act: Act, chapter: Chapter):
        scene_header = header_markdown(text=scene.scene_title, level=4)
        self.transcriber.run(content=scene_header)

        from crewai import Task
        task_description = f"""
            Write the scene for the novel with the following plot elements and characters:
            Plot: {scene.scene_plot}
            Characters: {scene.characters}

            Act description: {act.act_description}
            Act plot: {act.act_plot}
            Chapter description: {chapter.chapter_description}
            Chapter plot: {chapter.chapter_plot}
            Overall novel idea: {{idea}}

            Important:
            - Do not use any headings, just paragraphs.
            - Do not use em dashes.
        """
        task = Task(
            description=task_description.strip(),
            expected_output="A well-written scene in markdown format.",
            agent=self.author_agent
        )
        paragraphs = task.execute_sync().raw
        self.transcriber.run(content=f"{paragraphs}\n\n")

    def write_chapter(self, chapter: Chapter, act: Act):
        chapter_header = header_markdown(
            text=f"Chapter {self.chapter_number}: {chapter.chapter_title}", level=3
        )
        self.transcriber.run(content=chapter_header)

        if not self.disable_illustration:
            image_file = self.images_path / f"chapter_{self.chapter_number:02}.png"
            illustrator = IllustratorTool(filename=str(image_file))
            illustrator.run(
                prompt=f"Create an illustration for the chapter titled '{chapter.chapter_title}' with description "
                       f"'{chapter.chapter_description}'. IMPORTANT: Do not include any words, just an illustration. "
                       f"Here is some additional information from the art director: {self.artistic_vision}."
            )
            # Markdown path should stay relative
            relative_image_path = image_file.relative_to(self.output_path)
            image_md = image_markdown(image_path=str(relative_image_path), alt_text=f"Chapter {self.chapter_number} Illustration")
            self.transcriber.run(content=image_md)

        self.chapter_number += 1

        for scene in chapter.scenes:
            self.write_scene(scene, act, chapter)

        self.transcriber.run(content=add_page_break())

    def write_act(self, act: Act):
        act_header = header_markdown(text=f"Act {act.act_number}: {act.act_title}", level=2)
        self.transcriber.run(content=act_header)

        for chapter in act.chapters:
            self.write_chapter(chapter, act)

    def write_book_cover(self, book_info: Book):
        if not self.disable_illustration:
            cover_image = self.images_path / "cover.png"
            illustrator = IllustratorTool(filename=str(cover_image), size='1024x1536')
            illustrator.run(
                prompt=f"Create a book cover for the book titled '{book_info.title}', by author {book_info.author}, "
                       f"with description '{book_info.description}'. Here is some additional information from the "
                       f"art director: {self.artistic_vision}."
            )
            image_md = image_markdown(image_path=str(cover_image.relative_to(self.output_path)), alt_text="Book Cover")
            self.transcriber.run(content=image_md)

        title_md = header_markdown(text=book_info.title, level=1)
        self.transcriber.run(content=title_md)

    def save_pdf(self):
        self.pdf_tool.run(
            markdown_path=str(self.book_md_path),
            output_pdf_path=str(self.book_pdf_path)
        )
