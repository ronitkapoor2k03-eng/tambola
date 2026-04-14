import random
from utils import generate_ticket, check_jaldi5, check_line, check_four_corners, check_full_house

class Player:
    def __init__(self, name):
        self.name = name
        self.ticket = generate_ticket()
        self.marked_numbers = []
        self.marked_history = []
        self.is_winner = False
        self.won_patterns = []
    
    def mark_number(self, number):
        if number in self.ticket and number not in self.marked_numbers:
            self.marked_numbers.append(number)
            self.marked_history.append(number)
            return True
        return False
    
    def undo_last_mark(self):
        if self.marked_history:
            last = self.marked_history.pop()
            self.marked_numbers.remove(last)
            return True
        return False

class TambolaGame:
    def __init__(self, room_code):
        self.room_code = room_code
        self.players = {}
        self.called_numbers = []
        self.available_numbers = list(range(1, 91))
        self.game_started = False
        self.game_completed = False
        self.winners = []
    
    def add_player(self, name, player):
        if name not in self.players:
            self.players[name] = player
            return True
        return False
    
    def remove_player(self, name):
        if name in self.players:
            del self.players[name]
            return True
        return False
    
    def call_number(self):
        if not self.available_numbers:
            return None
        
        number = random.choice(self.available_numbers)
        self.available_numbers.remove(number)
        self.called_numbers.append(number)
        
        # Auto-mark for all players
        for player in self.players.values():
            if not player.is_winner:
                player.mark_number(number)
        
        return number
    
    def check_all_winners(self):
        winners_found = []
        
        for player_name, player in self.players.items():
            if player.is_winner:
                continue
            
            # Check Jaldi 5
            if "Jaldi 5" not in player.won_patterns:
                if check_jaldi5(player.ticket, player.marked_numbers) == 0:
                    player.won_patterns.append("Jaldi 5")
                    winners_found.append((player_name, "Jaldi 5"))
            
            # Check lines
            for line_num in range(3):
                line_name = ["Top Line", "Middle Line", "Bottom Line"][line_num]
                if line_name not in player.won_patterns:
                    if check_line(player.ticket, player.marked_numbers, line_num) == 0:
                        player.won_patterns.append(line_name)
                        winners_found.append((player_name, line_name))
            
            # Check four corners
            if "Four Corners" not in player.won_patterns:
                if check_four_corners(player.ticket, player.marked_numbers) == 0:
                    player.won_patterns.append("Four Corners")
                    winners_found.append((player_name, "Four Corners"))
            
            # Check full house
            if "Full House" not in player.won_patterns:
                if check_full_house(player.ticket, player.marked_numbers) == 0:
                    player.won_patterns.append("Full House")
                    player.is_winner = True
                    winners_found.append((player_name, "Full House"))
        
        return winners_found
    
    def reset_game(self):
        self.called_numbers = []
        self.available_numbers = list(range(1, 91))
        self.game_started = False
        self.game_completed = False
        self.winners = []
        
        for player in self.players.values():
            player.ticket = generate_ticket()
            player.marked_numbers = []
            player.marked_history = []
            player.is_winner = False
            player.won_patterns = []
