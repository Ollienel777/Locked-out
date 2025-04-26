from random import choice, randint
import json
import os
import random

DATA_FILE = "user_data.json"

activities = {
            "Creativity": [
                "Acrylic Painting", "Oil pastel", "Digital art", "Sketching", "Graphic design", "Baking", "Cooking", "Photography/Photo editing", "Videography/Video editing", "Collage", "Knitting/Crochet/Embroidery", "Make accessories", "Origami", "Journaling", "Singing", "Rapping", "Poetry writing", "Gardening", "Calligraphy", "Beatboxing", "Penbeat", "Songwriting/Composing", "Creative writing", "Drama/Acting/Monologues (recreate a scene from your favourite show!)"
            ],
            "Skill-building": [
                "Juggling","Rubix Cubing","Magic Tricks","Card Manipulation","Coding","Chess"
            ],
            "Physical/Well-being":[
                "Cardio (Jump roping, running)","Dance","HIIT Workouts","Stretching/Yoga","Frisbee"
            ],
            "Leisure":[
                "Play a new boardgame","Start a new show/movie","Find new artists/listen to new songs"
            ],
            "Learning":[
                "New language", "Wikepedia Page Marathon","Learn Morse Code", "Learn a sentence in Sign Language", "Start a new book"
            ],
            "Social": [
                "Join a new server of interest", "Participate in a micrograme with a group of friends (e.g. pictionary)", "Host a small call with friends and check in with them", "Challenge friends to trivia", "Play co-op games", "Make a collaborative playlist", "Have an award ceremony with friends (e.g. most likely to...)"
            ]
        }

def load_user_data():
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'w') as f:
            json.dump({}, f)

    with open(DATA_FILE, 'r') as f:
        return json.load(f)

def save_user_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=4)


def create_user_profile(username: str) -> str:
    data = load_user_data()

    if username in data:
        return f"{username}, you already have a profile!"

    # Create a new profile structure
    data[username] = {
        "total_exp": 0,
        "strands": {},
        "activities": {}
    }

    # Initialize strands
    for strand in activities.keys():
        data[username]["strands"][strand] = 0

    # Initialize individual activities
    for strand, acts in activities.items():
        for act in acts:
            data[username]["activities"][act] = 0

    save_user_data(data)
    return f"{username}, your profile has been created! Let's start earning EXP! 🎯"



def get_response(user_input: str, username: str = "") -> str:
    lowered: str = user_input.lower()

    if lowered.startswith('log') or lowered.startswith('l'):
        

        return 'hello :)'
    
    if lowered.startswith('profile'):
        return create_user_profile(username)
    
    if lowered.startswith('activity'):
        
        #strand = lowered[2]

        #display possible category to user
        def activity_selector():
            print("Choose a strand from the following options:")
            print("1. Creativity")
            print("2. Skill-building")
            print("3. Physical/Well-being")
            print("4. Leisure")
            print("5. Reading/Learning")
            print("6. Social")
        
        activity_input = input("Choose your preferred category of activity for today: ")

        #match input number to strand
        allstrands = {
            "1": "Creativity",
            "2": "Skill-building",
            "3": "Physical/Well-being",
            "4": "Leisure",
            "5": "Reading/Learning",
            "6": "Social"
        }
        
        #define strand as user's choice 
        strand = allstrands.get(activity_input)

        #generate random activity
        def daily_activity(strand): 
            if strand in activities:
                activity_choice = random.sample(activities[strand], 2)
                return activity_choice
            else:
                return f"Sorry, '{strand}' is not a valid category. Please type choice from categories 1-6. "
        
        #return daily activity generator
        

