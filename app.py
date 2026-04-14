def generate_proper_ticket():
    """Generate a VALID Tambola ticket following all rules"""
    ticket = [[0 for _ in range(9)] for _ in range(3)]
    
    # Column ranges
    col_ranges = [
        list(range(1, 10)),      # Column 1: 1-9
        list(range(10, 20)),     # Column 2: 10-19
        list(range(20, 30)),     # Column 3: 20-29
        list(range(30, 40)),     # Column 4: 30-39
        list(range(40, 50)),     # Column 5: 40-49
        list(range(50, 60)),     # Column 6: 50-59
        list(range(60, 70)),     # Column 7: 60-69
        list(range(70, 80)),     # Column 8: 70-79
        list(range(80, 91))      # Column 9: 80-90
    ]
    
    # Step 1: Decide how many numbers in each column (1-3 numbers per column)
    # Total must be 15 numbers across all columns
    column_counts = []
    remaining = 15
    for col in range(9):
        # Last column gets whatever remains
        if col == 8:
            count = remaining
        else:
            # Random between 1 and min(3, remaining - (8 - col))
            max_count = min(3, remaining - (8 - col))
            min_count = 1
            count = random.randint(min_count, max_count)
        column_counts.append(count)
        remaining -= count
    
    # Step 2: For each column, select random numbers and assign to rows
    for col in range(9):
        # Get random numbers from column range
        available_numbers = col_ranges[col].copy()
        selected_numbers = sorted(random.sample(available_numbers, column_counts[col]))
        
        # Get random rows for these numbers (1-3 numbers can be in any rows)
        rows = sorted(random.sample([0, 1, 2], column_counts[col]))
        
        # Assign numbers to rows (sorted top to bottom)
        for i, row in enumerate(rows):
            ticket[row][col] = selected_numbers[i]
    
    # Step 3: Ensure each row has exactly 5 numbers
    for row in range(3):
        current_count = len([ticket[row][col] for col in range(9) if ticket[row][col] != 0])
        
        if current_count > 5:
            # Remove extras
            filled_cols = [col for col in range(9) if ticket[row][col] != 0]
            to_remove = current_count - 5
            remove_cols = random.sample(filled_cols, to_remove)
            for col in remove_cols:
                ticket[row][col] = 0
        
        elif current_count < 5:
            # Add numbers to empty columns where possible
            empty_cols = [col for col in range(9) if ticket[row][col] == 0]
            needed = 5 - current_count
            
            # Filter columns that can accept more numbers (less than 3 already)
            valid_cols = []
            for col in empty_cols:
                col_count = len([ticket[r][col] for r in range(3) if ticket[r][col] != 0])
                if col_count < 3:
                    valid_cols.append(col)
            
            if len(valid_cols) >= needed:
                add_cols = random.sample(valid_cols, needed)
                for col in add_cols:
                    # Find a number not already used in this column
                    used_numbers = [ticket[r][col] for r in range(3) if ticket[r][col] != 0]
                    available = [n for n in col_ranges[col] if n not in used_numbers]
                    if available:
                        ticket[row][col] = random.choice(available)
    
    # Step 4: Sort numbers in each column top to bottom
    for col in range(9):
        col_numbers = []
        col_positions = []
        for row in range(3):
            if ticket[row][col] != 0:
                col_numbers.append(ticket[row][col])
                col_positions.append(row)
        
        # Sort numbers and their positions
        sorted_pairs = sorted(zip(col_numbers, col_positions))
        
        # Clear the column
        for row in range(3):
            ticket[row][col] = 0
        
        # Place sorted numbers back
        for i, (num, row) in enumerate(sorted_pairs):
            ticket[row][col] = num
    
    return ticket
