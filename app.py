import streamlit as st
import pandas as pd
import random
import string
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="Tambola (Housie) Game",
    page_icon="🎮",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .stApp {
        background-color: #f5f5f5;
    }
    
    /* House Board Styling */
    .house-board {
        background: white;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin: 10px 0;
        cursor: default;
    }
    
    .board-number {
        display: inline-block;
        width: 55px;
        height: 55px;
        margin: 3px;
        text-align: center;
        line-height: 55px;
        border-radius: 8px;
        font-weight: bold;
        font-size: 16px;
        cursor: default;
        transition: all 0.2s;
    }
    
    .board-number:hover {
        cursor: default;
    }
    
    /* Number colors based on tens */
    .num-1 { background-color: #FF6B6B; color: white; }
    .num-2 { background-color: #FFA07A; color: white; }
    .num-3 { background-color: #FFD93D; color: #333; }
    .num-4 { background-color: #6BCB77; color: white; }
    .num-5 { background-color: #4D96FF; color: white; }
    .num-6 { background-color: #9B59B6; color: white; }
    .num-7 { background-color: #FF9F9F; color: white; }
    .num-8 { background-color: #A8E6CF; color: #333; }
    .num-9 { background-color: #FFDAC1; color: #333; }
    .num-0 { background-color: #E0E0E0; color: #333; }
    
    .called-number-board {
        background-color: #2ECC71;
        color: white;
        transform: scale(1.05);
        box-shadow: 0 0 10px rgba(46,204,113,0.5);
    }
    
    /* Ticket Styling */
    .ticket {
        background: white;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin: 10px 0;
    }
    
    .ticket-number {
        display: inline-block;
        width: 50px;
        height: 50px;
        margin: 2px;
        text-align: center;
        line-height: 50px;
        border-radius: 6px;
        font-weight: bold;
        cursor: pointer;
        transition: all 0.2s;
    }
    
    .ticket-number-unmarked {
        background-color: #f8f9fa;
        border: 2px solid #dee2e6;
        color: #333;
    }
    
    .ticket-number-unmarked:hover {
        background-color: #e9ecef;
        cursor: pointer;
    }
    
    .ticket-number-marked {
        background-color: #28a745;
        border: 2px solid #28a745;
        color: white;
        cursor: default;
    }
    
    .ticket-number-empty {
        background-color: #f8f9fa;
        border: 2px solid #f8f9fa;
        color: transparent;
        cursor: default;
    }
    
    /* Chat Styling */
    .chat-container {
        background: white;
        border-radius: 10px;
        padding: 10px;
        height: 400px;
        overflow-y: auto;
        border: 1px solid #dee2e6;
    }
    
    .chat-message {
        background-color: #f8f9fa;
        padding: 8px 12px;
        margin: 8px 0;
        border-radius: 8px;
        border-left: 3px solid #007bff;
    }
    
    .chat-message strong {
        color: #007bff;
    }
    
    /* Player Card */
    .player-card {
        background: white;
        padding: 10px;
        margin: 8px 0;
        border-radius: 8px;
        border-left: 4px solid #007bff;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    
    .host-badge {
        background-color: #ff9800;
        color: white;
        padding: 2px 10px;
        border-radius: 12px;
        font-size: 11px;
        margin-left: 8px;
        display: inline-block;
    }
    
    .winner-badge {
        background-color: #28a745;
        color: white;
        padding: 2px 10px;
        border-radius: 12px;
        font-size: 11px;
        margin-left: 8px;
        display: inline-block;
    }
    
    /* Progress Box */
    .progress-box {
        background: white;
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
        border: 1px solid #dee2e6;
    }
    
    /* Button Styling */
    .stButton > button {
        background-color: #007bff;
        color: white;
        border: none;
        padding: 10px 20px;
        border-radius: 8px;
        font-weight: bold;
        transition: all 0.2s;
    }
    
    .stButton > button:hover {
        background-color: #0056b3;
        transform: translateY(-1px);
    }
    
    /* Disclaimer */
    .disclaimer {
        background-color: #fff3cd;
        border-left: 4px solid #ffc107;
        padding: 10px;
        margin: 10px 0;
        border-radius: 5px;
        font-size: 12px;
    }
    
    /* Section Headers */
    .section-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 10px;
        border-radius: 8px;
        margin: 15px 0 10px 0;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
def init_session():
    if 'game_state' not in st.session_state:
        st.session_state.game_state = {
            'room_code': None,
            'host': None,
            'players': {},
            'game_started': False,
            'called_numbers': [],
            'available_numbers': list(range(1, 91)),
            'chat_messages': [],
            'game_completed': False,
            'show_progress': True
        }
    if 'current_player' not in st.session_state:
        st.session_state.current_player = None
    if 'joined_room' not in st.session_state:
        st.session_state.joined_room = False
    if 'is_host' not in st.session_state:
        st.session_state.is_host = False

init_session()

def generate_proper_ticket():
    """Generate a proper Tambola ticket (3x9 grid with column constraints)"""
    ticket = [[0 for _ in range(9)] for _ in range(3)]
    
    # Column ranges: 1-9, 10-19, 20-29, 30-39, 40-49, 50-59, 60-69, 70-79, 80-90
    col_ranges = [
        (1, 9), (10, 19), (20, 29), (30, 39), (40, 49),
        (50, 59), (60, 69), (70, 79), (80, 90)
    ]
    
    # Each column must have exactly 3 numbers (some may be 0 in rows)
    for col in range(9):
        # Generate 3 random numbers for this column
        start, end = col_ranges[col]
        numbers = sorted(random.sample(range(start, end + 1), 3))
        
        # Randomly assign to rows
        rows = random.sample([0, 1, 2], 3)
        for i, row in enumerate(rows):
            ticket[row][col] = numbers[i]
    
    # Ensure each row has exactly 5 numbers
    for row in range(3):
        # Count numbers in row
        numbers_in_row = [ticket[row][col] for col in range(9) if ticket[row][col] != 0]
        
        # If more than 5, randomly remove extras
        while len(numbers_in_row) > 5:
            # Find a column to clear
            filled_cols = [col for col in range(9) if ticket[row][col] != 0]
            if filled_cols:
                col_to_clear = random.choice(filled_cols)
                ticket[row][col_to_clear] = 0
                numbers_in_row = [ticket[row][col] for col in range(9) if ticket[row][col] != 0]
        
        # If less than 5, add numbers from empty columns
        empty_cols = [col for col in range(9) if ticket[row][col] == 0]
        while len(numbers_in_row) < 5 and empty_cols:
            col = random.choice(empty_cols)
            start, end = col_ranges[col]
            
            # Check if column already has 3 numbers
            col_numbers = [ticket[r][col] for r in range(3) if ticket[r][col] != 0]
            if len(col_numbers) < 3:
                # Generate a number not already in column
                available = list(range(start, end + 1))
                for num in col_numbers:
                    if num in available:
                        available.remove(num)
                
                if available:
                    ticket[row][col] = random.choice(available)
                    numbers_in_row = [ticket[row][col] for col in range(9) if ticket[row][col] != 0]
                    empty_cols = [col for col in range(9) if ticket[row][col] == 0]
    
    return ticket

def get_number_color_class(num):
    """Get CSS class for number based on its tens digit"""
    tens = num // 10
    if tens == 0:
        return 'num-1'
    elif tens == 1:
        return 'num-2'
    elif tens == 2:
        return 'num-3'
    elif tens == 3:
        return 'num-4'
    elif tens == 4:
        return 'num-5'
    elif tens == 5:
        return 'num-6'
    elif tens == 6:
        return 'num-7'
    elif tens == 7:
        return 'num-8'
    elif tens == 8:
        return 'num-9'
    else:
        return 'num-0'

def check_line(ticket, marked, line_num):
    """Check if a specific line is complete"""
    line = ticket[line_num]
    numbers = [n for n in line if n != 0]
    remaining = len([n for n in numbers if n not in marked])
    return remaining

def check_four_corners(ticket, marked):
    """Check if four corners are marked"""
    corners = [ticket[0][0], ticket[0][8], ticket[2][0], ticket[2][8]]
    corners = [c for c in corners if c != 0]
    remaining = len([c for c in corners if c not in marked])
    return remaining

def check_full_house(ticket, marked):
    """Check if all numbers are marked"""
    all_numbers = [n for row in ticket for n in row if n != 0]
    remaining = len([n for n in all_numbers if n not in marked])
    return remaining

# Title
st.title("🎮 Tambola (Housie) Game")
st.markdown("*Play with friends and family - Traditional Tambola experience!*")

# Sidebar
with st.sidebar:
    st.markdown("### 👤 Your Profile")
    
    if not st.session_state.joined_room:
        player_name = st.text_input("Enter your name:", key="player_name_input")
        
        if player_name and st.button("Continue", use_container_width=True):
            st.session_state.current_player = player_name
            st.rerun()
    else:
        st.success(f"✅ Playing as: **{st.session_state.current_player}**")
        if st.session_state.is_host:
            st.markdown('<span class="host-badge">👑 HOST</span>', unsafe_allow_html=True)
        
        if st.session_state.game_state['game_started']:
            current_data = st.session_state.game_state['players'].get(st.session_state.current_player)
            if current_data and current_data.get('is_winner'):
                st.markdown('<span class="winner-badge">🏆 WINNER</span>', unsafe_allow_html=True)
        
        # Leave room button
        if st.button("🚪 Leave Room", use_container_width=True):
            if st.session_state.current_player in st.session_state.game_state['players']:
                del st.session_state.game_state['players'][st.session_state.current_player]
            
            if st.session_state.is_host and st.session_state.game_state['players']:
                new_host = list(st.session_state.game_state['players'].keys())[0]
                st.session_state.game_state['host'] = new_host
                st.session_state.is_host = (st.session_state.current_player == new_host)
            
            st.session_state.joined_room = False
            st.session_state.is_host = False
            st.rerun()
    
    st.markdown("---")
    st.markdown("### 📢 Legal Disclaimer")
    st.markdown("""
    <div class="disclaimer">
    ⚠️ This is a <strong>free-to-play</strong> social Tambola game.<br>
    • No real money involved<br>
    • No betting or gambling<br>
    • For entertainment only
    </div>
    """, unsafe_allow_html=True)

# Main content - Name entry required first
if not st.session_state.current_player:
    st.info("👋 **Welcome to Tambola!** Please enter your name in the sidebar to continue.")
    
    # Show game instructions
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("### 🎯 How to Play")
        st.markdown("""
        1. **Create or join a room**
        2. **Wait for host to start**
        3. **Click numbers on your ticket** as they're called
        4. **Win patterns** like lines, corners, full house
        """)
    with col2:
        st.markdown("### 🏆 Winning Patterns")
        st.markdown("""
        • **Jaldi 5** - First 5 numbers in any row
        • **Top/Middle/Bottom Line**
        • **Four Corners**
        • **Full House** (Multiple winners allowed)
        """)
    with col3:
        st.markdown("### 🎮 Features")
        st.markdown("""
        • **Real Tambola tickets** (3x9 grid)
        • **Colored house board**
        • **Chat with emojis**
        • **Progress tracking**
        • **Play with computer**
        """)

elif not st.session_state.joined_room:
    # Room creation/joining screen
    st.markdown("## 🎮 Join or Create a Game")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🏠 Create Room")
        st.markdown("Create a new room and become the host")
        if st.button("➕ Create Room", use_container_width=True):
            room_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
            st.session_state.game_state = {
                'room_code': room_code,
                'host': st.session_state.current_player,
                'players': {},
                'game_started': False,
                'called_numbers': [],
                'available_numbers': list(range(1, 91)),
                'chat_messages': [],
                'game_completed': False,
                'show_progress': True
            }
            st.session_state.game_state['players'][st.session_state.current_player] = {
                'name': st.session_state.current_player,
                'ticket': generate_proper_ticket(),
                'marked': [],
                'history': [],
                'is_winner': False,
                'won_patterns': []
            }
            st.session_state.joined_room = True
            st.session_state.is_host = True
            st.rerun()
    
    with col2:
        st.markdown("### 🔗 Join Room")
        room_code_input = st.text_input("Enter Room Code:", max_chars=6).upper()
        
        if st.button("🔍 Join Room", use_container_width=True) and room_code_input:
            st.session_state.game_state = {
                'room_code': room_code_input,
                'host': "Host",
                'players': {},
                'game_started': False,
                'called_numbers': [],
                'available_numbers': list(range(1, 91)),
                'chat_messages': [],
                'game_completed': False,
                'show_progress': True
            }
            st.session_state.game_state['players'][st.session_state.current_player] = {
                'name': st.session_state.current_player,
                'ticket': generate_proper_ticket(),
                'marked': [],
                'history': [],
                'is_winner': False,
                'won_patterns': []
            }
            st.session_state.joined_room = True
            st.session_state.is_host = False
            st.rerun()

else:
    # Game interface
    game = st.session_state.game_state
    current_player_data = game['players'].get(st.session_state.current_player)
    
    # Room header
    st.markdown(f"### 🎲 Room Code: **{game['room_code']}**")
    
    # Player list and controls row
    col_players, col_controls = st.columns([2, 1])
    
    with col_players:
        st.markdown("#### 👥 Players in Room")
        for player_name, player_data in game['players'].items():
            host_tag = " 👑" if player_name == game['host'] else ""
            winner_tag = " 🏆" if player_data.get('is_winner', False) else ""
            st.markdown(f'<div class="player-card">🎮 {player_name}{host_tag}{winner_tag}</div>', unsafe_allow_html=True)
    
    with col_controls:
        if not game['game_started']:
            # Computer player option (only for host)
            if st.session_state.is_host:
                if st.button("🤖 Add Computer Player", use_container_width=True):
                    comp_name = f"Computer_{len(game['players'])}"
                    game['players'][comp_name] = {
                        'name': comp_name,
                        'ticket': generate_proper_ticket(),
                        'marked': [],
                        'history': [],
                        'is_winner': False,
                        'won_patterns': []
                    }
                    st.rerun()
            
            # Start game button (only host)
            if st.session_state.is_host and len(game['players']) >= 1:
                if st.button("🚀 START GAME", use_container_width=True, type="primary"):
                    game['game_started'] = True
                    st.rerun()
            elif not st.session_state.is_host:
                st.info("⏳ Waiting for host to start the game...")
        else:
            if st.session_state.is_host and not game['game_completed']:
                if st.button("🎲 CALL NEXT NUMBER", use_container_width=True, type="primary"):
                    if game['available_numbers']:
                        number = random.choice(game['available_numbers'])
                        game['available_numbers'].remove(number)
                        game['called_numbers'].append(number)
                        
                        # Auto-mark for all non-winner players
                        for player in game['players'].values():
                            if not player['is_winner']:
                                flat_ticket = [num for row in player['ticket'] for num in row]
                                if number in flat_ticket and number not in player['marked']:
                                    player['marked'].append(number)
                                    player['history'].append(number)
                        st.rerun()
                    else:
                        st.warning("All numbers called!")
                        game['game_completed'] = True
    
    if game['game_started']:
        st.markdown("---")
        
        # Main game area
        col_left, col_right = st.columns([2, 1])
        
        with col_left:
            # House Board (Read-only, visible to all)
            st.markdown('<div class="section-header">🏠 TAMBOLA HOUSE BOARD</div>', unsafe_allow_html=True)
            st.markdown('<div class="house-board">', unsafe_allow_html=True)
            
            # Display 1-90 in a 9x10 grid
            for row in range(9):
                cols_html = ""
                for col in range(10):
                    num = row * 10 + col + 1
                    is_called = num in game['called_numbers']
                    color_class = get_number_color_class(num)
                    called_class = " called-number-board" if is_called else ""
                    cols_html += f'<div class="board-number {color_class}{called_class}">{num}</div>'
                st.markdown(f'<div style="display: flex; justify-content: center;">{cols_html}</div>', unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Called numbers list
            st.markdown('<div class="section-header">📢 Recently Called Numbers</div>', unsafe_allow_html=True)
            if game['called_numbers']:
                recent_numbers = game['called_numbers'][-20:]
                recent_html = ""
                for num in recent_numbers:
                    color_class = get_number_color_class(num)
                    recent_html += f'<div class="board-number {color_class}" style="width: 45px; height: 45px; line-height: 45px; display: inline-block;">{num}</div>'
                st.markdown(recent_html, unsafe_allow_html=True)
            else:
                st.info("No numbers called yet. Host will start calling numbers!")
            
            # Player's Ticket
            if current_player_data and not current_player_data['is_winner']:
                st.markdown('<div class="section-header">🎟️ YOUR TICKET</div>', unsafe_allow_html=True)
                st.markdown('<div class="ticket">', unsafe_allow_html=True)
                
                ticket = current_player_data['ticket']
                marked = current_player_data['marked']
                
                for row in range(3):
                    cols = st.columns(9)
                    for col in range(9):
                        num = ticket[row][col]
                        if num != 0:
                            is_marked = num in marked
                            button_style = "ticket-number-marked" if is_marked else "ticket-number-unmarked"
                            
                            if cols[col].button(
                                str(num), 
                                key=f"ticket_{st.session_state.current_player}_{row}_{col}",
                                use_container_width=True,
                                disabled=is_marked
                            ):
                                if num not in current_player_data['marked']:
                                    current_player_data['marked'].append(num)
                                    current_player_data['history'].append(num)
                                    st.rerun()
                        else:
                            cols[col].markdown('<div class="ticket-number-empty">-</div>', unsafe_allow_html=True)
                
                st.markdown('</div>', unsafe_allow_html=True)
                
                # Undo button
                if st.button("↩️ Undo Last Mark"):
                    if current_player_data['history']:
                        last = current_player_data['history'].pop()
                        current_player_data['marked'].remove(last)
                        st.rerun()
                
                # Check for wins
                new_wins = []
                
                # Check Jaldi 5 (first 5 numbers in any row)
                for row in range(3):
                    row_numbers = [num for num in ticket[row] if num != 0][:5]
                    marked_in_row = [num for num in row_numbers if num in marked]
                    if len(marked_in_row) == 5 and "Jaldi 5" not in current_player_data['won_patterns']:
                        new_wins.append("Jaldi 5")
                
                # Check lines
                for line_num in range(3):
                    line_name = ["Top Line", "Middle Line", "Bottom Line"][line_num]
                    if line_name not in current_player_data['won_patterns']:
                        if check_line(ticket, marked, line_num) == 0:
                            new_wins.append(line_name)
                
                # Check four corners
                if "Four Corners" not in current_player_data['won_patterns']:
                    if check_four_corners(ticket, marked) == 0:
                        new_wins.append("Four Corners")
                
                # Check full house
                if "Full House" not in current_player_data['won_patterns']:
                    if check_full_house(ticket, marked) == 0:
                        new_wins.append("Full House")
                        current_player_data['is_winner'] = True
                
                # Announce wins
                for win in new_wins:
                    current_player_data['won_patterns'].append(win)
                    if win == "Full House":
                        st.success(f"🏆🏆🏆 CONGRATULATIONS! You won {win}! 🏆🏆🏆")
                        st.balloons()
                    else:
                        st.success(f"🎉 Congratulations! You won {win}! 🎉")
                        st.balloons()
                    
                    if new_wins:
                        st.rerun()
            
            elif current_player_data and current_player_data['is_winner']:
                st.success(f"🏆🏆🏆 WINNER! You won FULL HOUSE! 🏆🏆🏆")
                st.info("👀 You are now in spectator mode. Watch others play!")
        
        with col_right:
            # Progress tracking with toggle
            st.markdown('<div class="section-header">📊 Game Progress</div>', unsafe_allow_html=True)
            
            show_progress = st.checkbox("Show numbers remaining for patterns", value=game['show_progress'])
            game['show_progress'] = show_progress
            
            if show_progress and current_player_data and not current_player_data['is_winner']:
                st.markdown('<div class="progress-box">', unsafe_allow_html=True)
                
                ticket = current_player_data['ticket']
                marked = current_player_data['marked']
                
                # Jaldi 5 progress
                for row in range(3):
                    row_numbers = [num for num in ticket[row] if num != 0][:5]
                    marked_count = len([num for num in row_numbers if num in marked])
                    remaining = 5 - marked_count
                    if remaining == 0:
                        st.success(f"🎯 Jaldi 5 (Row {row+1}): ✅ COMPLETE!")
                    else:
                        st.info(f"🎯 Jaldi 5 (Row {row+1}): {remaining} numbers left")
                
                # Lines progress
                for line_num in range(3):
                    remaining = check_line(ticket, marked, line_num)
                    line_name = ["Top Line", "Middle Line", "Bottom Line"][line_num]
                    if remaining == 0:
                        st.success(f"📏 {line_name}: ✅ COMPLETE!")
                    else:
                        st.info(f"📏 {line_name}: {remaining} numbers left")
                
                # Four corners progress
                remaining_corners = check_four_corners(ticket, marked)
                if remaining_corners == 0:
                    st.success(f"🔲 Four Corners: ✅ COMPLETE!")
                else:
                    st.info(f"🔲 Four Corners: {remaining_corners} corners left")
                
                # Full house progress
                remaining_fh = check_full_house(ticket, marked)
                if remaining_fh == 0:
                    st.success(f"🏆 Full House: ✅ COMPLETE!")
                else:
                    st.info(f"🏆 Full House: {remaining_fh} numbers left")
                
                st.markdown('</div>', unsafe_allow_html=True)
            
            # Winners board
            st.markdown('<div class="section-header">🏆 Winners Board</div>', unsafe_allow_html=True)
            winners = [p for p in game['players'].values() if p.get('is_winner', False)]
            if winners:
                for i, winner in enumerate(winners[:4], 1):
                    st.markdown(f'<div class="winner-card" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 10px; border-radius: 10px; margin: 5px 0; color: white; text-align: center;">🥇 Full House #{i}: {winner["name"]}</div>', unsafe_allow_html=True)
            else:
                st.info("No winners yet")
            
            # Computer auto-call (if computer players exist)
            if st.session_state.is_host and game['game_started'] and not game['game_completed']:
                computer_players = [p for p in game['players'].values() if p['name'].startswith('Computer')]
                if computer_players:
                    auto_call = st.checkbox("🤖 Auto-call numbers (Computer mode)", value=False)
                    if auto_call and game['available_numbers']:
                        import time
                        number = random.choice(game['available_numbers'])
                        game['available_numbers'].remove(number)
                        game['called_numbers'].append(number)
                        
                        for player in game['players'].values():
                            if not player['is_winner']:
                                flat_ticket = [num for row in player['ticket'] for num in row]
                                if number in flat_ticket and number not in player['marked']:
                                    player['marked'].append(number)
                                    player['history'].append(number)
                        time.sleep(0.5)
                        st.rerun()
        
        # Chat section
        st.markdown("---")
        st.markdown('<div class="section-header">💬 Chat Room</div>', unsafe_allow_html=True)
        
        col_chat_input, col_emoji = st.columns([3, 1])
        
        with col_chat_input:
            chat_input = st.text_input("Type your message:", key="chat_input", placeholder="Say something...")
        with col_emoji:
            emoji = st.selectbox("😊", ["", "😂", "🎉", "🔥", "👏", "😎", "🥳", "😮", "🎯", "🏆"])
        
        if st.button("📤 Send Message", use_container_width=True):
            if chat_input or emoji:
                message = chat_input
                if emoji:
                    message += " " + emoji if message else emoji
                game['chat_messages'].append({
                    "player": st.session_state.current_player,
                    "message": message,
                    "time": datetime.now()
                })
                st.rerun()
        
        # Display chat messages
        chat_container = st.container()
        with chat_container:
            for msg in game['chat_messages'][-30:]:
                st.markdown(f'<div class="chat-message"><strong>{msg["player"]}:</strong> {msg["message"]}</div>', unsafe_allow_html=True)
        
        # New game button (host only)
        if st.session_state.is_host and (game['game_completed'] or len(game['called_numbers']) == 90):
            if st.button("🔄 Start New Game", use_container_width=True):
                game['game_started'] = False
                game['called_numbers'] = []
                game['available_numbers'] = list(range(1, 91))
                game['game_completed'] = False
                for player in game['players'].values():
                    player['ticket'] = generate_proper_ticket()
                    player['marked'] = []
                    player['history'] = []
                    player['is_winner'] = False
                    player['won_patterns'] = []
                st.rerun()

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; font-size: 12px;">
    <p>🎮 MVP (Minimum Viable Product) - Built by Ronit Kapoor</p>
    <p>Traditional Tambola (Housie) Game - Free to play, just for fun!</p>
</div>
""", unsafe_allow_html=True)
