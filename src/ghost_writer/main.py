#!/usr/bin/env python
import sys
import warnings

from datetime import datetime

from ghost_writer.crew import GhostWriter

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

# This main file is intended to be a way for you to run your
# crew locally, so refrain from adding unnecessary logic into this file.
# Replace with inputs you want to test with, it will automatically
# interpolate any tasks and agents information

def run():
    
    idea = """
    In a near-future world, an autistic scientist named Dr. Ada N. Sel—obsessed with patterns, vibration, 
    and the limits of perception—has created a revolutionary AI model capable of interpreting complex tactile 
    reverberations into human language. Socially reclusive but intellectually fierce, Ada has always felt more 
    comfortable communicating through indirect signals—vibrations in materials, variations in light, mathematical 
    symmetries. Her fascination with non-visual ways of knowing leads her to an astonishing discovery: deep beneath 
    the earth, a sentient worm named Caelum Lumbricus, who navigates existence entirely through pressure, tremor, and 
    temperature, is not only alive—but self-aware, poetic, and hungry for dialogue.

    Through a sensitive and tentative interface mediated by Ada’s AI, the two begin an unprecedented exchange. Ada 
    attempts to explain concepts like light, vision, sound, and color—experiences that Caelum has never known. 
    Caelum, in turn, speaks in metaphors of clay, compression, root warmth, decay, and the rhythmic press of the 
    earth, offering a philosophy of presence that challenges Ada’s scientific instincts.

    What begins as a research experiment becomes something more: a shared reverie about the boundaries of 
    consciousness, the nature of language, and the haunting question of what it means to truly connect across 
    radically different modes of being. As they struggle to find metaphors that bridge their worlds, both Ada and 
    Caelum are changed by the encounter—drawn into a mutual unearthing of selfhood, trust, and wonder.
    
    IMPORTANT: Avoid using em dashes. Use commas, periods, or parentheses instead depending on the context.
    """

    inputs = {
        'idea': idea,
        'author': 'Morgan Vale',
        'title': 'Tactile Reveries II: Of Silence and Substance'
    }
    
    try:
        GhostWriter().crew().kickoff(inputs=inputs)
    except Exception as e:
        raise Exception(f"An error occurred while running the crew: {e}")
