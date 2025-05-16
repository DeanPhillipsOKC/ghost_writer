from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task, before_kickoff
from crewai.agents.agent_builder.base_agent import BaseAgent
from ghost_writer.models import Idea, Plot, Characters, Chapter, Act, Scene, Book
from ghost_writer.tools.transcribe_tool import TranscribeTool
from ghost_writer.tools.illustrator_tool import IllustratorTool
from ghost_writer.tools.convert_to_pdf_tool import MarkdownToPDFTool
from typing import List
from pydantic import BaseModel
import shutil
import os

@CrewBase
class GhostWriter():
    """GhostWriter crew"""

    agents: List[BaseAgent]
    tasks: List[Task]
    artistic_vision: str = None

    PAGE_BREAK = "<div style=\"page-break-after: always;\"></div>"

    chapter_number: int = 1

    @before_kickoff
    def on_before_kickoff(self, inputs):
        # Delete the output directory if it exists
        shutil.rmtree('output', ignore_errors=True)
        os.makedirs('output/images', exist_ok=True)

        return inputs

    @agent
    def idea_developer(self) -> Agent:
        return Agent(
            config=self.agents_config['idea_developer'],
            verbose=True
        )

    @agent
    def plot_developer(self) -> Agent:
        return Agent(
            config=self.agents_config['plot_developer'], 
            verbose=True
        )
    
    @agent
    def character_developer(self) -> Agent:
        return Agent(
            config=self.agents_config['character_developer'],
            verbose=True
        )
    
    @agent
    def art_director(self) -> Agent:
        return Agent(
            config=self.agents_config['art_director'],
            verbose=True
        )
    
    @agent
    def outline_developer(self) -> Agent:
        return Agent(
            config=self.agents_config['outline_developer'],
            verbose=True
        )
    
    @agent
    def artist(self) -> Agent:
        return Agent(
            config=self.agents_config['artist'],
            verbose=True
        )
    
    @agent
    def author(self) -> Agent:
        return Agent(
            config=self.agents_config['author'],
            verbose=True
        )

    @task
    def ideation_task(self) -> Task:
        return Task(
            config=self.tasks_config['ideation_task'],
            output_pydantic=Idea,
        )
    
    @task
    def plot_development_task(self) -> Task:
        return Task(
            config=self.tasks_config['plot_development_task'],
            output_pydantic=Plot,
        )
    
    @task
    def character_development_task(self) -> Task:
        return Task(
            config=self.tasks_config['character_development_task'],
            output_pydantic=Characters,
        )
    
    def write_scene(self, scene: Scene, act: Act, chapter: Chapter):
        TranscribeTool().run(content = f"#### {scene.scene_title}\n\n")

        task = Task(
            description=f"Write the scene for the novel with the following plot elements, and characters \
                Plot: {scene.scene_plot} \
                Characters: {scene.characters} \
                \
                Act description for context: \
                {act.act_description} \
                \
                Act plot for context: \
                {act.act_plot} \
                \
                Chapter description for context: \
                {chapter.chapter_description} \
                \
                Chapter plot for context: \
                {chapter.chapter_plot} \
                \
                Overall novel idea for context: \
                {{idea}} \
                \
                Important: \
                - Do not use any headings just the paragraphs. \
                - Do not use em dashes unless absolutely necessary.",
            expected_output="A well-written scene that follows the outline and overall plot and ideas. Use markdown",
            agent=self.author(),
        )
        paragraphs = task.execute_sync().raw

        TranscribeTool().run(content = f"{paragraphs}\n\n")

    def write_chapter(self, chapter: Chapter, act: Act):
        TranscribeTool().run(content = f"### Chapter {self.chapter_number}: {chapter.chapter_title}\n\n")

        illustrator_tool = IllustratorTool(filename=f'output/images/chapter_{self.chapter_number:02}.png')
        illustrator_tool.run(
            prompt=f"Create an illustration for the chapter titled '{chapter.chapter_title}' with description \
                '{chapter.chapter_description}.  IMPORTANT: Do not include any words, just an illustration.' \
                    Here is some additional information from the art director that should be take into account: \
                        {self.artistic_vision}.")
        
        TranscribeTool().run(content = f"![Chapter {self.chapter_number} Illustration](images/chapter_{self.chapter_number:02}.png)\n\n")

        self.chapter_number += 1

        for scene in chapter.scenes:
            self.write_scene(scene, act, chapter)
            
        TranscribeTool().run(content = self.PAGE_BREAK)

    def write_act(self, act: Act):
        TranscribeTool().run(content = f"## Act {act.act_number}: {act.act_title}\n\n")

        for chapter in act.chapters:
            self.write_chapter(chapter, act)

    def on_act_created(self, task_output):
        act = task_output.pydantic
        self.write_act(act)

        pdf_tool = MarkdownToPDFTool()
        pdf_tool.run(
            markdown_path='output/book.md',
            output_pdf_path=f'output/book.pdf'
        )

    def on_book_created(self, task_output):
        book = task_output.pydantic

        illustrator_tool = IllustratorTool(filename='output/images/cover.png', size='1024x1536')
        illustrator_tool.run(
            prompt=f"Create a book cover for the book titled '{book.title}',  by author {book.author}, \
                with description '{book.description}'.  Here is some additional information from the \
                    art director that should be take into account: {self.artistic_vision}.")
        
        TranscribeTool().run(content = f"![Book Cover](images/cover.png)\n\n")
        TranscribeTool().run(content = f"# {book.title}\n*By {book.author}*\n\n")

    @task
    def book_development_task(self) -> Task:
        return Task(
            config=self.tasks_config['book_development_task'],
            output_pydantic=Book,
            callback=self.on_book_created,
        )

    def on_artistic_vision_created(self, task_output):
        self.artistic_vision = task_output.pydantic

    @task
    def artistic_vision_task(self) -> Task:
        return Task(
            config=self.tasks_config['artistic_vision_task'],
            output_pydantic=Book,
            callback=self.on_artistic_vision_created,
        )

    @task
    def act1_development_task(self) -> Task:
        return Task(
            config=self.tasks_config['act1_development_task'],
            output_pydantic=Act,
            callback=self.on_act_created,
        )
    
    @task
    def act2_development_task(self) -> Task:
        return Task(
            config=self.tasks_config['act2_development_task'],
            output_pydantic=Act,
            callback=self.on_act_created,
        )
    
    @task
    def act3_development_task(self) -> Task:
        return Task(
            config=self.tasks_config['act3_development_task'],
            output_pydantic=Act,
            callback=self.on_act_created,
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks, 
            process=Process.sequential,
            verbose=True,
            memory=True
        )
