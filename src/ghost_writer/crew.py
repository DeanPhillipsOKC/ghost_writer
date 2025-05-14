from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task, before_kickoff
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List
from pydantic import BaseModel
import shutil
import os

class Idea(BaseModel):
    """Idea for the novel"""
    premise: str
    theme: str
    characters: str
    plot_concepts: str

class Plot(BaseModel):
    """Plot for the novel"""
    description: str
    rising_action: str
    climax: str
    falling_action: str
    resolution: str

class Character(BaseModel):
    """Character for the novel"""
    name: str
    role: str
    traits: str
    backstory: str
    motivations: str
    flaws: str
    relationships: str

class Characters(BaseModel):
    """Characters for the novel"""
    characters: List[Character]

class Chapter(BaseModel):
    """Outline node for the novel"""
    chapter_number: int
    chapter_description: str
    characters: str
    plot: Plot

class Outline(BaseModel):
    chapters: List[Chapter]

@CrewBase
class GhostWriter():
    """GhostWriter crew"""

    agents: List[BaseAgent]
    tasks: List[Task]

    @before_kickoff
    def on_before_kickoff(self, inputs):
        # Delete the output directory if it exists
        shutil.rmtree('output', ignore_errors=True)
        os.makedirs('output', exist_ok=True)

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
            config=self.agents_config['idea_developer'], 
            verbose=True
        )
    
    @agent
    def character_developer(self) -> Agent:
        return Agent(
            config=self.agents_config['character_developer'],
            verbose=True
        )
    
    @agent
    def outline_developer(self) -> Agent:
        return Agent(
            config=self.agents_config['outline_developer'],
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
    
    def write_chapter(self, chapter: Chapter):
        task = Task(
            description=f"Write chapter {chapter.chapter_number} ({chapter.chapter_description}) \
                with characters {chapter.characters} and plot {chapter.plot.description}",
            expected_output="A well-written chapter that follows the outline and overall plot and ideas. Use markdown",
            agent=self.author(),
            output_file = f"output/chapter_{chapter.chapter_number:02}.md",
        )
        task.execute_sync()

    def on_outline_created(self, task_output):
        for chapter in task_output.pydantic.chapters:
            self.write_chapter(chapter)

    @task
    def outline_development_task(self) -> Task:
        return Task(
            config=self.tasks_config['outline_development_task'],
            output_pydantic=Outline,
            callback=self.on_outline_created,
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
