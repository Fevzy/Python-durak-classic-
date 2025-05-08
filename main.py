import random
import os
import time

# Определяем масти и значения карт
suits = ['♠', '♣', '♦', '♥']
ranks = ['6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']

# Создаем колоду карт
deck = [rank + suit for suit in suits for rank in ranks]
random.shuffle(deck)

# Раздаем карты игрокам
player_hand = deck[:6]
ai_hand = deck[6:12]
deck = deck[12:]

# Определяем козырь
trump_card = deck.pop()
trump_suit = trump_card[-1]

# ANSI-коды для цветов
RED = "\033[91m"
BLACK = "\033[30m"
WHITE = "\033[97m"
GREEN_BG = "\033[42m"
WHITE_BG = "\033[47m"
RESET = "\033[0m"

# Определяем цвет козыря и белый фон
trump_color = RED if trump_suit in ['♦', '♥'] else BLACK
trump_display = f"{WHITE_BG}{trump_color}[{trump_card[:-1]}{trump_suit}]{RESET}"  # Козырь на белом фоне

# Функция для очистки консоли
def clear_console():
    os.system('cls' if os.name == 'nt' else 'clear')

# Функция для отображения карт красиво с цветом
def format_card(card, trim_right=False, is_back=False):
    """Форматирует карту. Если is_back=True, то карта закрыта (рубашка зеленая с узором)."""
    if is_back:
        return [
            f"{GREEN_BG}┌───┐{RESET}",
            f"{GREEN_BG}│◆◇◆│{RESET}",
            f"{GREEN_BG}│◇◆◇│{RESET}",
            f"{GREEN_BG}└───┘{RESET}"
        ]

    if not card:
        return ["   ", "   ", "   ", "   "]  # Пустое место

    color = RED if card[-1] in ['♦', '♥'] else BLACK  # Черный цвет для ♠ и ♣
    rank, suit = card[:-1], card[-1]

    if trim_right:
        return [
            f"{WHITE_BG}{color}┌──{RESET}",
            f"{WHITE_BG}{color}│{rank:<2}{RESET}",
            f"{WHITE_BG}{color}│ {suit}{RESET}",
            f"{WHITE_BG}{color}└──{RESET}"
        ]

    return [
        f"{WHITE_BG}{color}┌───┐{RESET}",
        f"{WHITE_BG}{color}│{rank:<2} │{RESET}",
        f"{WHITE_BG}{color}│ {suit} │{RESET}",
        f"{WHITE_BG}{color}└───┘{RESET}"
    ]

# Функция для отображения игрового поля
def show_table(attack_card=None, defense_card=None, action_text="", trim_attack=False):
    clear_console()
    print("\n" + "=" * 50)
    print(f"Колода ({len(deck)} карт) | Козырь: {trump_display}")

    print("\nИИ карты:")
    ai_cards = [format_card(None, is_back=True) for _ in ai_hand]  # Закрытые карты ИИ
    for i in range(4):
        print(" ".join([card[i] for card in ai_cards]))

    print("\n" + "-" * 50)
    print(action_text.center(30))

    # Отображаем карты атаки и защиты
    attack_display = format_card(attack_card, trim_right=trim_attack) if attack_card else ["   ", "   ", "   ", "   "]
    defense_display = format_card(defense_card) if defense_card else ["", "", "", ""]

    for i in range(4):
        print(f"{attack_display[i]}{defense_display[i]}")

    print("\n" + "-" * 50)
    print("Ваши карты:")

    player_cards = [format_card(card) for card in player_hand]  # Открытые карты игрока

    # Отображаем карты в виде строк
    for i in range(4):
        print(" ".join([card[i] for card in player_cards]))

    # Добавляем нумерацию **под каждой картой**
    print(" ".join([f"  {idx + 1}  " for idx in range(len(player_hand))]))

    print("\n" + "=" * 50 + "\n")

# Определяем, кто ходит первым
def determine_first_turn():
    player_trumps = [card for card in player_hand if card[-1] == trump_suit]
    ai_trumps = [card for card in ai_hand if card[-1] == trump_suit]

    if player_trumps and ai_trumps:
        return "player" if min(player_trumps, key=lambda card: ranks.index(card[:-1])) < min(ai_trumps, key=lambda card: ranks.index(card[:-1])) else "ai"
    elif player_trumps:
        return "player"
    elif ai_trumps:
        return "ai"
    else:
        return random.choice(["player", "ai"])

# Основной игровой цикл
turn = determine_first_turn()

while player_hand and ai_hand:
    if turn == "player":
        show_table(None, None, "Ваш ход")

        try:
            choice = int(input("Выберите номер карты для атаки: ")) - 1
            if choice < 0 or choice >= len(player_hand):
                print("Неверный выбор!")
                continue
        except ValueError:
            print("Введите число!")
            continue

        attack_card = player_hand.pop(choice)

        show_table(attack_card, None, "Игрок атакует", trim_attack=False)
        time.sleep(1.5)

        # ИИ выбирает карту для защиты
        defense_card = None
        for card in ai_hand:
            if (card[-1] == attack_card[-1] and ranks.index(card[:-1]) > ranks.index(attack_card[:-1])) or (card[-1] == trump_suit and attack_card[-1] != trump_suit):
                defense_card = card
                break

        if defense_card:
            ai_hand.remove(defense_card)
            show_table(attack_card, defense_card, "ИИ защищается", trim_attack=True)
            time.sleep(1.5)
            turn = "ai"
        else:
            show_table(attack_card, None, "ИИ берет карту")
            ai_hand.append(attack_card)
            time.sleep(1.5)
            turn = "player"

    else:
        if ai_hand:
            attack_card = random.choice(ai_hand)
            ai_hand.remove(attack_card)
            show_table(attack_card, None, "ИИ атакует")
            time.sleep(1.5)

            show_table(attack_card, None, "Выберите карту для защиты или введите '0', чтобы взять карту")

            while True:
                try:
                    choice = int(input("Введите номер карты для защиты: ")) - 1
                    if choice == -1:
                        show_table(attack_card, None, "Вы взяли карту")
                        player_hand.append(attack_card)
                        time.sleep(1.5)
                        turn = "ai"
                        break
                    elif choice < 0 or choice >= len(player_hand):
                        print("Неверный выбор!")
                        continue
                    defense_card = player_hand[choice]
                    if (defense_card[-1] == attack_card[-1] and ranks.index(defense_card[:-1]) > ranks.index(attack_card[:-1])) or (defense_card[-1] == trump_suit and attack_card[-1] != trump_suit):
                        player_hand.remove(defense_card)
                        show_table(attack_card, defense_card, "Игрок защищается", trim_attack=True)
                        time.sleep(1.5)
                        turn = "player"
                        break
                    else:
                        print("Этой картой нельзя отбиться!")
                except ValueError:
                    print("Введите число!")

    while deck and len(player_hand) < 6:
        player_hand.append(deck.pop())
    while deck and len(ai_hand) < 6:
        ai_hand.append(deck.pop())

    time.sleep(1.5)

if not player_hand:
    print("Вы победили!")
elif not ai_hand:
    print("ИИ победил!")