from random import choice, randint

def get_response(user_input: str, username: str = "") -> str:
    lowered: str = user_input.lower()

    if lowered == 'hihi':
        return 'hello :)'

    if 'roll dice' in lowered:
        return f'you rolled: {randint(1, 6)}'

    if lowered.startswith('activity'):
        return f"{username} ...."

    return "I didn't understand that. Try saying '$hihi' or '$roll dice'."

