import random
from enum import IntEnum
from statistics import mode
import xml.etree.ElementTree as ET

class GameAction(IntEnum):
    Rock = 0
    Paper = 1
    Scissors = 2
    Lizard = 3
    Spock = 4


class GameResult(IntEnum):
    Victory = 0
    Defeat = 1
    Tie = 2


# Diccionario global para almacenar las reglas cargadas del XML
# Formato: {(Ganador, Perdedor): "Descripción de la victoria"}
VICTORY_RULES = {}

NUMBER_RECENT_ACTIONS = 5


def load_rules_from_xml(file_path):
    """Carga las reglas de victoria desde un archivo XML."""
    try:
        tree = ET.parse(file_path)  #
        root = tree.getroot()  #

        rules = {}
        for victory in root.findall('victory'):  #
            winner_name = victory.get('choice')
            loser_name = victory.get('against')
            description = victory.text.strip()

            # Convertimos los nombres de texto a miembros d el Enum GameAction
            winner = GameAction[winner_name]
            loser = GameAction[loser_name]

            rules[(winner, loser)] = description

        return rules
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo {file_path}")
        return {}
    except KeyError as e:
        print(f"Error: El nombre {e} en el XML no coincide con el Enum GameAction")
        return {}

# Cargamos las reglas al inicio
VICTORY_RULES = load_rules_from_xml('victories.xml')

def assess_game(user_action, computer_action):
    if user_action == computer_action:
        print(f"Both players picked {user_action.name}. Draw game!")
        return GameResult.Tie

    # Verificamos si la combinación (usuario, computadora) existe en nuestras reglas de victoria
    if (user_action, computer_action) in VICTORY_RULES:
        print(f"{VICTORY_RULES[(user_action, computer_action)]}. You won!")
        return GameResult.Victory
    else:
        # Si no ganó el usuario y no es empate, ganó la computadora
        # Buscamos la descripción en el sentido inverso (computadora, usuario)
        desc = VICTORY_RULES.get((computer_action, user_action), "Computer wins")
        print(f"{desc}. You lost!")
        return GameResult.Defeat

def get_computer_action(user_actions_history):
    if not user_actions_history:
        computer_action = get_random_computer_action()
    else:
        # AI: Elige algo que gane al movimiento más frecuente del usuario
        most_frequent_recent_action = GameAction(mode(user_actions_history[-NUMBER_RECENT_ACTIONS:]))
        computer_action = get_winner_action(most_frequent_recent_action)

    print(f"Computer picked {computer_action.name}.")
    return computer_action


def get_user_action():
    # Se genera dinámicamente: Rock[0], Paper[1], Scissors[2], Lizard[3], Spock[4]
    game_choices = [f"{action.name}[{action.value}]" for action in GameAction]
    game_choices_str = ", ".join(game_choices)
    user_selection = int(input(f"\nPick a choice ({game_choices_str}): "))
    return GameAction(user_selection)


def get_random_computer_action():
    return GameAction(random.randint(0, len(GameAction) - 1))


def get_winner_action(target_action):
    """
    Busca en las reglas qué acciones ganan contra una acción específica.
    En la versión de 5 opciones, hay dos opciones que ganan a cada una.
    """
    possible_winners = [winner for (winner, loser) in VICTORY_RULES.keys() if loser == target_action]
    return random.choice(possible_winners) if possible_winners else get_random_computer_action()

def play_another_round():
        another_round = input("\nAnother round? (y/n): ")
        return another_round.lower() == 'y'


def main():
    if not VICTORY_RULES:
        print("Could not load rules. Exiting.")
        return

    user_actions_history = []

    while True:
        try:
            user_action = get_user_action()
            user_actions_history.append(user_action)
        except (ValueError, IndexError):
            range_str = f"[0, {len(GameAction) - 1}]"
            print(f"Invalid selection. Pick a choice in range {range_str}!")
            continue

        computer_action = get_computer_action(user_actions_history)
        assess_game(user_action, computer_action)

        if not play_another_round():
            break


if __name__ == "__main__":
    main()
