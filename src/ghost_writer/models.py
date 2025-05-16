from pydantic import BaseModel
from typing import List

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

class Scene(BaseModel):
    """Scene for the novel"""
    scene_description: str
    scene_title: str
    characters: str
    scene_plot: str
    
class Chapter(BaseModel):
    """Outline node for the novel"""
    chapter_title: str
    chapter_description: str
    chapter_plot: str
    scenes: List[Scene]

class Act(BaseModel):
    """Act for the novel"""
    act_number: int
    act_title: str
    act_description: str
    act_plot: str
    chapters: List[Chapter]

class Book(BaseModel):
    title: str
    author: str
    description: str

class ArtisticVision(BaseModel):
    """Artistic vision for the novel"""
    genre: str
    tone: str
    style: str
    themes: str
    target_audience: str
    visual_elements: str
    color_palette: str
    mood_board: str