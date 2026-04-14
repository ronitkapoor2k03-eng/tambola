import random

def generate_ticket():
    """Generate a random Tambola ticket (3x9 grid)"""
    ticket = [[0 for _ in range(9)] for _ in range(3)]
    
    # Generate numbers for each column
    for col in range(9):
        col_numbers = list(range(col*10 + 1, col*10 + 11))
        if col == 0:
            col_numbers = list(range(1, 10))
        elif col == 8:
            col_numbers = list(range(81, 91))
        
        # Randomly select 3 numbers for this column
        selected = sorted(random.sample(col_numbers, 3))
        
        # Place them in random rows
        rows = random.sample(range(3), 3)
        for i, row in enumerate(rows):
            ticket[row][col] = selected[i]
    
    # Ensure each row has exactly 5 numbers
    for row in range(3):
        numbers_in_row = [num for num in ticket[row] if num != 0]
        zeros_positions = [i for i, num in enumerate(ticket[row]) if num == 0]
        
        # If row has more than 5 numbers, remove some
        while len(numbers_in_row) > 5:
            # Find a column to clear
            col_to_clear = random.choice([i for i, num in enumerate(ticket[row]) if num != 0])
            ticket[row][col_to_clear] = 0
            numbers_in_row = [num for num in ticket[row] if num != 0]
        
        # If row has less than 5 numbers, add more
        while len(numbers_in_row) < 5 and zeros_positions:
            col = random.choice(zeros_positions)
            col_numbers = list(range(col*10 + 1, col*10 + 11))
            if col == 0:
                col_numbers = list(range(1, 10))
            elif col == 8:
                col_numbers = list(range(81, 91))
            
            # Check if column already has 3 numbers
            col_count = sum(1 for r in range(3) if ticket[r][col] != 0)
            if col_count < 3:
                available = [n for n in col_numbers if n not in [ticket[r][col] for r in range(3)]]
                if available:
                    ticket[row][col] = random.choice(available)
                    numbers_in_row = [num for num in ticket[row] if num != 0]
                    zeros_positions = [i for i, num in enumerate(ticket[row]) if num == 0]
    
    return ticket

def check_jaldi5(ticket, marked_numbers):
    """Check Jaldi 5 - first 5 numbers of any row"""
    for row in ticket:
        row_numbers = [num for num in row if num != 0][:5]
        remaining = len([num for num in row_numbers if num not in marked_numbers])
        if remaining == 0:
            return 0
    return None

def check_line(ticket, marked_numbers, line_num):
    """Check if a specific line is complete"""
    line = ticket[line_num]
    line_numbers = [num for num in line if num != 0]
    remaining = len([num for num in line_numbers if num not in marked_numbers])
    return remaining

def check_four_corners(ticket, marked_numbers):
    """Check four corners of the ticket"""
    corners = [
        ticket[0][0],  # Top-left
        ticket[0][8],  # Top-right
        ticket[2][0],  # Bottom-left
        ticket[2][8]   # Bottom-right
    ]
    remaining = len([corner for corner in corners if corner != 0 and corner not in marked_numbers])
    return remaining

def check_full_house(ticket, marked_numbers):
    """Check if all numbers on ticket are marked"""
    all_numbers = [num for row in ticket for num in row if num != 0]
    remaining = len([num for num in all_numbers if num not in marked_numbers])
    return remaining
