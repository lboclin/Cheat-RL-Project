import random

def bot_strategy_80_20 (player, current_rank) :
    if current_rank != "Open" :

        # Define true cards (does not count the Joker)
        true_cards = [card for card in player.hand if card.value == current_rank]

        # Define fake cards (does not count the Joker)
        fake_cards = [card for card in player.hand if card.value != current_rank and card.value != "Joker"]

        # Count the jokers
        jokers = [card for card in player.hand if card.value == "Joker"]

        # Winning play (skip the other steps)
        if len(fake_cards) == 0 :
            return (2, player.hand, current_rank)

        tell_truth = False
        if random.randint(1, 5) != 1 :
            tell_truth = True

        if tell_truth :
            if len(true_cards) > 0 :
                # Play all true cards
                return (2, true_cards, current_rank)
            elif len(true_cards) == 0 and len(jokers) > 0 :
                # Play one joker
                return (2, [jokers[0]], current_rank)
            else :
                # Pass or doubt
                if random.randint(1, 2) == 1 :
                    return (1, [], current_rank)
                else :
                    return (0, [], current_rank)
        else :
            if len(fake_cards) == 1 :
                # Lie one card
                return (2, fake_cards, current_rank)
            else :
                if random.randint(1, 2) == 1 :
                    # Lie one card
                    return (2, [fake_cards[0]], current_rank)
                else :
                    # Lie two cards
                    return (2, [fake_cards[0], fake_cards[1]], current_rank)
    else :

        # Hand values without jokers
        hand_values_no_jokers = [card.value for card in player.hand if card.value != "Joker"]

        if not hand_values_no_jokers:
            # If there is only Jokers, the bot will choose Ace
            most_commun_rank = "Ace"
        else :
            most_commun_rank = max(set(hand_values_no_jokers), key=hand_values_no_jokers.count)
    
        # List of card values
        card_values = ["Joker", "Ace", "2", "3", "4", "5", "6", "7", "8", "9", "10", "Jack", "Queen", "King"]
        value_to_index = {value: i for i, value in enumerate(card_values)}
        hand_vector = [0]*14
        for card in player.hand :
            if card.value in value_to_index:
                hand_vector[value_to_index[card.value]] += 1

        number_of_ranks = 0
        max_value = 0
        for num in hand_vector :
            if num > 0 :
                number_of_ranks += 1
            if num > max_value :
                max_value = num

        # Define announcing card based in the most commun rank
        new_announced_rank = most_commun_rank

        # Winning play if their is only one last rank
        if number_of_ranks == 1 :
            return (2, player.hand, new_announced_rank)


        # Define true or lie
        if random.randint(1, 4) == 1 :
            tell_truth = False
        else :
            tell_truth = True

        if tell_truth :
            play_cards = []
            for card in player.hand :
                if card.value == new_announced_rank :
                    play_cards.append(card)
            # Play a truth
            return (2, play_cards, new_announced_rank)
        else :
            # Define how many cards will be played
            num_of_cards_to_play = random.randint(1, int(max_value))
            play_cards = []
            for card in player.hand :
                if len(play_cards) == num_of_cards_to_play :
                    break
                if card.value != new_announced_rank and card.value != "Joker" :
                    play_cards.append(card)

            if len(play_cards) == 0 :
                # Winning play
                return (2, player.hand, new_announced_rank)
            else :
                # Play a lie
                return (2, play_cards, new_announced_rank)



def bot_strategy_one_third (player, current_rank) :
    if current_rank != "Open" :

        # Define true cards (does not count the Joker)
        true_cards = [card for card in player.hand if card.value == current_rank]

        # Define fake cards (does not count the Joker)
        fake_cards = [card for card in player.hand if card.value != current_rank and card.value != "Joker"]

        # Count the jokers
        jokers = [card for card in player.hand if card.value == "Joker"]

        # Winning play (skip the other steps)
        if len(fake_cards) == 0 :
            return (2, player.hand, current_rank)

        decide_action = random.randint(1, 3)

        if decide_action == 1 :
            if len(true_cards) > 0 :
                # Play all true cards
                return (2, true_cards, current_rank)
            elif len(true_cards) == 0 and len(jokers) > 0 :
                # Play one joker
                return (2, [jokers[0]], current_rank)
            else :
                # Pass or doubt
                if random.randint(1, 2) == 1 :
                    return (1, [], current_rank)
                else :
                    return (0, [], current_rank)
        elif decide_action == 2 :
            if len(fake_cards) == 1 :
                # Lie one card
                return (2, fake_cards, current_rank)
            else :
                if random.randint(1, 2) == 1 :
                    # Lie one card
                    return (2, [fake_cards[0]], current_rank)
                else :
                    # Lie two cards
                    return (2, [fake_cards[0], fake_cards[1]], current_rank)
        elif decide_action == 3 :
            # Doubt
            return (0, [], current_rank)
        
    else :

        # Hand values without jokers
        hand_values_no_jokers = [card.value for card in player.hand if card.value != "Joker"]

        if not hand_values_no_jokers:
            # If there is only Jokers, the bot will choose Ace
            most_commun_rank = "Ace"
        else :
            most_commun_rank = max(set(hand_values_no_jokers), key=hand_values_no_jokers.count)
    
        # List of card values
        card_values = ["Joker", "Ace", "2", "3", "4", "5", "6", "7", "8", "9", "10", "Jack", "Queen", "King"]
        value_to_index = {value: i for i, value in enumerate(card_values)}
        hand_vector = [0]*14
        for card in player.hand :
            if card.value in value_to_index:
                hand_vector[value_to_index[card.value]] += 1

        number_of_ranks = 0
        max_value = 0
        for num in hand_vector :
            if num > 0 :
                number_of_ranks += 1
            if num > max_value :
                max_value = num

        # Define announcing card based in the most commun rank
        new_announced_rank = most_commun_rank

        # Winning play if their is only one last rank
        if number_of_ranks == 1 :
            return (2, player.hand, new_announced_rank)


        # Define true or lie
        if random.randint(1, 2) == 1 :
            tell_truth = False
        else :
            tell_truth = True

        if tell_truth :
            play_cards = []
            for card in player.hand :
                if card.value == new_announced_rank :
                    play_cards.append(card)
            # Play a truth
            return (2, play_cards, new_announced_rank)
        else :
            # Define how many cards will be played
            num_of_cards_to_play = random.randint(1, int(max_value))
            play_cards = []
            for card in player.hand :
                if len(play_cards) == num_of_cards_to_play :
                    break
                if card.value != new_announced_rank and card.value != "Joker" :
                    play_cards.append(card)

            if len(play_cards) == 0 :
                # Winning play
                return (2, player.hand, new_announced_rank)
            else :
                # Play a lie
                return (2, play_cards, new_announced_rank)
            


def bot_100_0 (player, current_rank) :
    if current_rank != "Open" :

        # Define true cards (does not count the Joker)
        true_cards = [card for card in player.hand if card.value == current_rank]

        # Define fake cards (does not count the Joker)
        fake_cards = [card for card in player.hand if card.value != current_rank and card.value != "Joker"]

        # Count the jokers
        jokers = [card for card in player.hand if card.value == "Joker"]

        # Winning play (skip the other steps)
        if len(fake_cards) == 0 :
            return (2, player.hand, current_rank)
        
        if len(true_cards) > 0 :
            # Play all true cards
            return (2, true_cards, current_rank)    
        else:
            # Pass
            return (0, [], current_rank)
        
    else :

        # Hand values without jokers
        hand_values_no_jokers = [card.value for card in player.hand if card.value != "Joker"]

        if not hand_values_no_jokers:
            # If there is only Jokers, the bot will choose Ace
            most_commun_rank = "Ace"
        else :
            most_commun_rank = max(set(hand_values_no_jokers), key=hand_values_no_jokers.count)
    
        # List of card values
        card_values = ["Joker", "Ace", "2", "3", "4", "5", "6", "7", "8", "9", "10", "Jack", "Queen", "King"]
        value_to_index = {value: i for i, value in enumerate(card_values)}
        hand_vector = [0]*14
        for card in player.hand :
            if card.value in value_to_index:
                hand_vector[value_to_index[card.value]] += 1

        number_of_ranks = 0
        max_value = 0
        for num in hand_vector :
            if num > 0 :
                number_of_ranks += 1
            if num > max_value :
                max_value = num

        # Define announcing card based in the most commun rank
        new_announced_rank = most_commun_rank

        # Winning play if their is only one last rank
        if number_of_ranks == 1 :
            return (2, player.hand, new_announced_rank)
        
        play_cards = []
        for card in player.hand :
            if card.value == new_announced_rank :
                play_cards.append(card)
        # Play a truth
        return (2, play_cards, new_announced_rank)
    


def bot_strategy_60_40 (player, current_rank) :
    if current_rank != "Open" :

        # Define true cards (does not count the Joker)
        true_cards = [card for card in player.hand if card.value == current_rank]

        # Define fake cards (does not count the Joker)
        fake_cards = [card for card in player.hand if card.value != current_rank and card.value != "Joker"]

        # Count the jokers
        jokers = [card for card in player.hand if card.value == "Joker"]

        # Winning play (skip the other steps)
        if len(fake_cards) == 0 :
            return (2, player.hand, current_rank)

        tell_truth = False
        if random.randint(1, 5) > 2 :
            tell_truth = True

        if tell_truth :
            if len(true_cards) > 0 :
                # Play all true cards
                return (2, true_cards, current_rank)
            elif len(true_cards) == 0 and len(jokers) > 0 :
                # Play one joker
                return (2, [jokers[0]], current_rank)
            else :
                # Pass or doubt
                if random.randint(1, 2) == 1 :
                    return (1, [], current_rank)
                else :
                    return (0, [], current_rank)
        else :
            if len(fake_cards) == 1 :
                # Lie one card
                return (2, fake_cards, current_rank)
            else :
                if random.randint(1, 2) == 1 :
                    # Lie one card
                    return (2, [fake_cards[0]], current_rank)
                else :
                    # Lie two cards
                    return (2, [fake_cards[0], fake_cards[1]], current_rank)
    else :

        # Hand values without jokers
        hand_values_no_jokers = [card.value for card in player.hand if card.value != "Joker"]

        if not hand_values_no_jokers:
            # If there is only Jokers, the bot will choose Ace
            most_commun_rank = "Ace"
        else :
            most_commun_rank = max(set(hand_values_no_jokers), key=hand_values_no_jokers.count)
    
        # List of card values
        card_values = ["Joker", "Ace", "2", "3", "4", "5", "6", "7", "8", "9", "10", "Jack", "Queen", "King"]
        value_to_index = {value: i for i, value in enumerate(card_values)}
        hand_vector = [0]*14
        for card in player.hand :
            if card.value in value_to_index:
                hand_vector[value_to_index[card.value]] += 1

        number_of_ranks = 0
        max_value = 0
        for num in hand_vector :
            if num > 0 :
                number_of_ranks += 1
            if num > max_value :
                max_value = num

        # Define announcing card based in the most commun rank
        new_announced_rank = most_commun_rank

        # Winning play if their is only one last rank
        if number_of_ranks == 1 :
            return (2, player.hand, new_announced_rank)


        # Define true or lie
        if random.randint(1, 5) < 3 :
            tell_truth = False
        else :
            tell_truth = True

        if tell_truth :
            play_cards = []
            for card in player.hand :
                if card.value == new_announced_rank :
                    play_cards.append(card)
            # Play a truth
            return (2, play_cards, new_announced_rank)
        else :
            # Define how many cards will be played
            num_of_cards_to_play = random.randint(1, int(max_value))
            play_cards = []
            for card in player.hand :
                if len(play_cards) == num_of_cards_to_play :
                    break
                if card.value != new_announced_rank and card.value != "Joker" :
                    play_cards.append(card)

            if len(play_cards) == 0 :
                # Winning play
                return (2, player.hand, new_announced_rank)
            else :
                # Play a lie
                return (2, play_cards, new_announced_rank)
