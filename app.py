import streamlit as st
import pandas as pd
import random
import string
from datetime import datetime
import base64

# Page configuration
st.set_page_config(
    page_title="Tambola (Housie) Game",
    page_icon="🎮",
    layout="wide"
)

# Custom CSS for proper ticket display
st.markdown("""
<style>
    .stApp {
        background-color: #f0f2f6;
    }
    
    /* House Board Styling */
    .house-board {
        background: white;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin: 10px 0;
    }
    
    .board-number {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 55px;
        height: 55px;
        margin: 3px;
        text-align: center;
        border-radius: 8px;
        font-weight: bold;
        font-size: 16px;
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
        background-color: #2ECC71 !important;
        color: white !important;
        transform: scale(1.05);
        box-shadow: 0 0 10px rgba(46,204,113,0.5);
    }
    
    /* Ticket Styling - FIXED for proper grid */
    .ticket-container {
        background: white;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin: 10px 0;
        overflow-x: auto;
    }
    
    .ticket-table {
        width: 100%;
        border-collapse: collapse;
    }
    
    .ticket-table td {
        border: 2px solid #dee2e6;
        text-align: center;
        vertical-align: middle;
        padding: 0;
    }
    
    .ticket-number-btn {
        width: 100%;
        height: 55px;
        background-color: #f8f9fa;
        border: none;
        font-size: 18px;
        font-weight: bold;
        cursor: pointer;
        transition: all 0.2s;
        font-family: monospace;
    }
    
    .ticket-number-btn:hover:not(:disabled) {
        background-color: #e9ecef;
        transform: scale(0.98);
    }
    
    .ticket-number-marked {
        background-color: #28a745 !important;
        color: white !important;
        cursor: default;
    }
    
    .ticket-number-empty {
        background-color: #f8f9fa;
        color: #ccc;
        cursor: default;
    }
    
    /* Player Card */
    .player-card {
        background: white;
        padding: 12px;
        margin: 8px 0;
        border-radius: 10px;
        border-left: 4px solid #007bff;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    
    .player-name {
        font-size: 16px;
        font-weight: 500;
    }
    
    .host-badge {
        background-color: #ff9800;
        color: white;
        padding: 2px 10px;
        border-radius: 12px;
        font-size: 11px;
        margin-left: 8px;
    }
    
    .winner-badge {
        background-color: #28a745;
        color: white;
        padding: 2px 10px;
        border-radius: 12px;
        font-size: 11px;
        margin-left: 8px;
    }
    
    /* Chat Styling */
    .chat-container {
        background: white;
        border-radius: 10px;
        padding: 10px;
        height: 350px;
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
    
    /* Progress Box */
    .progress-box {
        background: white;
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
        border: 1px solid #dee2e6;
    }
    
    /* Announcement animation */
    @keyframes slideIn {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    .announcement {
        animation: slideIn 0.5s ease-out;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
        text-align: center;
        font-size: 24px;
        font-weight: bold;
    }
    
    .disclaimer {
        background-color: #fff3cd;
        border-left: 4px solid #ffc107;
        padding: 10px;
        margin: 10px 0;
        border-radius: 5px;
        font-size: 12px;
    }
    
    .section-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 10px;
        border-radius: 8px;
        margin: 15px 0 10px 0;
        font-weight: bold;
    }
    
    button {
        background-color: #007bff;
        color: white;
        border: none;
        padding: 10px 20px;
        border-radius: 8px;
        font-weight: bold;
        cursor: pointer;
    }
    
    button:hover {
        background-color: #0056b3;
    }
</style>
""", unsafe_allow_html=True)

# Voice announcement function
def get_number_announcement(number):
    """Get fun Tambola announcement for a number"""
    announcements = {
        1: "Number 1 - Ek number!",
        2: "Number 2 - Swan!",
        3: "Number 3 - Tiranga!",
        4: "Number 4 - Choupatti!",
        5: "Number 5 - High Five!",
        6: "Number 6 - Half a dozen!",
        7: "Number 7 - Lucky seven!",
        8: "Number 8 - Ashta Lakshmi!",
        9: "Number 9 - Naveen!",
        10: "Number 10 - Perfect ten!",
        11: "Number 11 - Two thin legs!",
        12: "Number 12 - One dozen!",
        13: "Number 13 - Unlucky for some!",
        14: "Number 14 - Valentine's!",
        15: "Number 15 - Teenage!",
        16: "Number 16 - Sweet sixteen!",
        17: "Number 17 - Dancing queen!",
        18: "Number 18 - Coming of age!",
        19: "Number 19 - Good night!",
        20: "Number 20 - Twenty!",
        21: "Number 21 - Key of door!",
        22: "Number 22 - Two little ducks!",
        23: "Number 23 - Thee and me!",
        24: "Number 24 - Two dozen!",
        25: "Number 25 - Silver jubilee!",
        26: "Number 26 - Bed and breakfast!",
        27: "Number 27 - Gateway to heaven!",
        28: "Number 28 - Over weight!",
        29: "Number 29 - Rise and shine!",
        30: "Number 30 - Dirty thirty!",
        31: "Number 31 - Get up and run!",
        32: "Number 32 - Buckle my shoe!",
        33: "Number 33 - Dirty knees!",
        34: "Number 34 - Ask for more!",
        35: "Number 35 - Jump and jive!",
        36: "Number 36 - Three dozen!",
        37: "Number 37 - More than eleven!",
        38: "Number 38 - Christmas cake!",
        39: "Number 39 - Famous steps!",
        40: "Number 40 - Life begins!",
        41: "Number 41 - Time for fun!",
        42: "Number 42 - Winnie the Pooh!",
        43: "Number 43 - Down on your knees!",
        44: "Number 44 - All the fours!",
        45: "Number 45 - Halfway there!",
        46: "Number 46 - Up to tricks!",
        47: "Number 47 - Four and seven!",
        48: "Number 48 - Four dozen!",
        49: "Number 49 - Rise and shine!",
        50: "Number 50 - Half century!",
        51: "Number 51 - Tweak of the thumb!",
        52: "Number 52 - Weeks in a year!",
        53: "Number 53 - Here comes Hans!",
        54: "Number 54 - Clean the floor!",
        55: "Number 55 - All the fives!",
        56: "Number 56 - Was she worth it?",
        57: "Number 57 - Heinz varieties!",
        58: "Number 58 - Make them wait!",
        59: "Number 59 - Brighton line!",
        60: "Number 60 - Three score!",
        61: "Number 61 - Bakers bun!",
        62: "Number 62 - Turn the screw!",
        63: "Number 63 - Tickle me!",
        64: "Number 64 - Red raw!",
        65: "Number 65 - Old age pension!",
        66: "Number 66 - Clickety click!",
        67: "Number 67 - Made in heaven!",
        68: "Number 68 - Saving grace!",
        69: "Number 69 - Favourite of mine!",
        70: "Number 70 - Three score ten!",
        71: "Number 71 - Bang on the drum!",
        72: "Number 72 - Six dozen!",
        73: "Number 73 - Queen bee!",
        74: "Number 74 - Hit the floor!",
        75: "Number 75 - Strive and strive!",
        76: "Number 76 - Trombones!",
        77: "Number 77 - Two little crutches!",
        78: "Number 78 - Heavens gate!",
        79: "Number 79 - One more time!",
        80: "Number 80 - Gandhi's number!",
        81: "Number 81 - Stop and run!",
        82: "Number 82 - Old Father Time!",
        83: "Number 83 - Time for tea!",
        84: "Number 84 - Seven dozen!",
        85: "Number 85 - Staying alive!",
        86: "Number 86 - Between the sticks!",
        87: "Number 87 - Torquay in Devon!",
        88: "Number 88 - Two fat ladies!",
        89: "Number 89 - Nearly there!",
        90: "Number 90 - Top of the house!"
    }
    return announcements.get(number, f"Number {number}")

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
            'show_progress': True,
            'last_announcement': None,
            'voice_enabled': True
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
    
    # First, put 3 numbers in each column
    for col in range(9):
        start, end = col_ranges[col]
        numbers = sorted(random.sample(range(start, end + 1), 3))
        rows = random.sample([0, 1, 2], 3)
        for i, row in enumerate(rows):
            ticket[row][col] = numbers[i]
    
    # Ensure each row has exactly 5 numbers
    for row in range(3):
        numbers_in_row = [ticket[row][col] for col in range(9) if ticket[row][col] != 0]
        
        # If more than 5, randomly remove extras
        while len(numbers_in_row) > 5:
            filled_cols = [col for col in range(9) if ticket[row][col] != 0]
            if filled_cols:
                col_to_clear = random.choice(filled_cols)
                ticket[row][col_to_clear] = 0
                numbers_in_row = [ticket[row][col] for col in range(9) if ticket[row][col] != 0]
        
        # If less than 5, add numbers
        while len(numbers_in_row) < 5:
            empty_cols = [col for col in range(9) if ticket[row][col] == 0]
            if empty_cols:
                col = random.choice(empty_cols)
                start, end = col_ranges[col]
                
                # Check column count
                col_numbers = [ticket[r][col] for r in range(3) if ticket[r][col] != 0]
                if len(col_numbers) < 3:
                    available = list(range(start, end + 1))
                    for num in col_numbers:
                        if num in available:
                            available.remove(num)
                    
                    if available:
                        ticket[row][col] = random.choice(available)
                        numbers_in_row = [ticket[row][col] for col in range(9) if ticket[row][col] != 0]
    
    return ticket

def get_number_color_class(num):
    tens = num // 10 if num < 90 else 9
    return f'num-{tens}'

def check_line(ticket, marked, line_num):
    line = ticket[line_num]
    numbers = [n for n in line if n != 0]
    remaining = len([n for n in numbers if n not in marked])
    return remaining

def check_four_corners(ticket, marked):
    corners = [ticket[0][0], ticket[0][8], ticket[2][0], ticket[2][8]]
    corners = [c for c in corners if c != 0]
    remaining = len([c for c in corners if c not in marked])
    return remaining

def check_full_house(ticket, marked):
    all_numbers = [n for row in ticket for n in row if n != 0]
    remaining = len([n for n in all_numbers if n not in marked])
    return remaining

# Title
st.title("🎮 Tambola (Housie) Game")
st.markdown("*Play with friends and family - With fun voice announcements!*")

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
        
        # Voice toggle
        voice_enabled = st.checkbox("🔊 Voice Announcements", value=st.session_state.game_state['voice_enabled'])
        st.session_state.game_state['voice_enabled'] = voice_enabled
        
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
    ⚠️ <strong>Free-to-play social game</strong><br>
    • No real money involved<br>
    • No betting or gambling<br>
    • For entertainment only
    </div>
    """, unsafe_allow_html=True)

# Main content
if not st.session_state.current_player:
    st.info("👋 **Welcome to Tambola!** Please enter your name in the sidebar to continue.")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("### 🎯 How to Play")
        st.markdown("""
        1. **Create or join a room**
        2. **Share room code with friends**
        3. **Host starts the game**
        4. **Click numbers on your ticket**
        5. **Win patterns!**
        """)
    with col2:
        st.markdown("### 🏆 Winning Patterns")
        st.markdown("""
        • **Jaldi 5** - First 5 in any row
        • **Top/Middle/Bottom Line**
        • **Four Corners**
        • **Full House** (Multiple winners)
        """)
    with col3:
        st.markdown("### 🎮 Features")
        st.markdown("""
        • **Voice announcements** 🎤
        • **Real Tambola tickets**
        • **Live chat with emojis**
        • **Progress tracking**
        • **Play with computer**
        """)

elif not st.session_state.joined_room:
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
                'show_progress': True,
                'last_announcement': None,
                'voice_enabled': True
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
            # In MVP, we'll create a new game state for the joiner
            # In production, this would fetch from a central server
            st.session_state.game_state = {
                'room_code': room_code_input,
                'host': "Host",  # This would come from server
                'players': {},
                'game_started': False,
                'called_numbers': [],
                'available_numbers': list(range(1, 91)),
                'chat_messages': [],
                'game_completed': False,
                'show_progress': True,
                'last_announcement': None,
                'voice_enabled': True
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
    game = st.session_state.game_state
    current_player_data = game['players'].get(st.session_state.current_player)
    
    # Show room info and player list prominently
    st.markdown(f"## 🎲 Room: **{game['room_code']}**")
    
    # Player list - everyone can see everyone
    st.markdown("### 👥 Players in Room")
    player_cols = st.columns(min(len(game['players']), 4))
    for idx, (player_name, player_data) in enumerate(game['players'].items()):
        col_idx = idx % 4
        with player_cols[col_idx]:
            host_tag = " 👑" if player_name == game['host'] else ""
            winner_tag = " 🏆" if player_data.get('is_winner', False) else ""
            st.markdown(f'<div class="player-card"><span class="player-name">🎮 {player_name}{host_tag}{winner_tag}</span></div>', unsafe_allow_html=True)
    
    # Show current player status
    if current_player_data and current_player_data.get('is_winner', False):
        st.success(f"🏆🏆🏆 {st.session_state.current_player}, you are a WINNER! 🏆🏆🏆")
    
    # Host controls
    if not game['game_started']:
        col_controls, col_computer = st.columns(2)
        
        with col_controls:
            if st.session_state.is_host and len(game['players']) >= 1:
                if st.button("🚀 START GAME", use_container_width=True, type="primary"):
                    game['game_started'] = True
                    st.rerun()
            elif not st.session_state.is_host:
                st.info(f"⏳ Waiting for host ({game['host']}) to start the game...")
        
        with col_computer:
            if st.session_state.is_host and not game['game_started']:
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
    
    if game['game_started']:
        st.markdown("---")
        
        # Show last announcement
        if game['last_announcement']:
            st.markdown(f'<div class="announcement">🎤 {game["last_announcement"]}</div>', unsafe_allow_html=True)
        
        # Main game area
        col_left, col_right = st.columns([2, 1])
        
        with col_left:
            # House Board
            st.markdown('<div class="section-header">🏠 TAMBOLA HOUSE BOARD</div>', unsafe_allow_html=True)
            st.markdown('<div class="house-board">', unsafe_allow_html=True)
            
            for row in range(9):
                cols_html = ""
                for col in range(10):
                    num = row * 10 + col + 1
                    is_called = num in game['called_numbers']
                    color_class = get_number_color_class(num)
                    called_class = " called-number-board" if is_called else ""
                    cols_html += f'<div class="board-number {color_class}{called_class}">{num}</div>'
                st.markdown(f'<div style="display: flex; justify-content: center; flex-wrap: wrap;">{cols_html}</div>', unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Called numbers
            st.markdown('<div class="section-header">📢 Recently Called Numbers</div>', unsafe_allow_html=True)
            if game['called_numbers']:
                recent_numbers = game['called_numbers'][-20:]
                recent_html = ""
                for num in recent_numbers:
                    color_class = get_number_color_class(num)
                    recent_html += f'<div class="board-number {color_class}" style="width: 45px; height: 45px; line-height: 45px; display: inline-flex;">{num}</div>'
                st.markdown(recent_html, unsafe_allow_html=True)
            else:
                st.info("No numbers called yet. Host will start calling numbers!")
            
            # Player's Ticket - FIXED proper grid display
            if current_player_data and not current_player_data['is_winner']:
                st.markdown('<div class="section-header">🎟️ YOUR TICKET</div>', unsafe_allow_html=True)
                st.markdown('<div class="ticket-container">', unsafe_allow_html=True)
                
                ticket = current_player_data['ticket']
                marked = current_player_data['marked']
                
                # Create HTML table for ticket
                html_table = '<table class="ticket-table" style="width: 100%; border-collapse: collapse;">'
                for row in range(3):
                    html_table += '<tr>'
                    for col in range(9):
                        num = ticket[row][col]
                        if num != 0:
                            is_marked = num in marked
                            if is_marked:
                                html_table += f'<td style="border: 2px solid #dee2e6; padding: 0;"><button class="ticket-number-btn ticket-number-marked" disabled style="width: 100%; height: 55px;">{num}</button></td>'
                            else:
                                html_table += f'<td style="border: 2px solid #dee2e6; padding: 0;"><button class="ticket-number-btn" onclick="alert(\'Use Streamlit buttons instead\')" style="width: 100%; height: 55px;">{num}</button></td>'
                        else:
                            html_table += f'<td style="border: 2px solid #dee2e6; padding: 0;"><div class="ticket-number-empty" style="width: 100%; height: 55px; display: flex; align-items: center; justify-content: center;">-</div></td>'
                    html_table += '</tr>'
                html_table += '</table>'
                
                st.markdown(html_table, unsafe_allow_html=True)
                
                # Use Streamlit buttons for actual interaction
                st.markdown("**Click numbers below to mark them:**")
                for row in range(3):
                    cols = st.columns(9)
                    for col in range(9):
                        num = ticket[row][col]
                        if num != 0 and num not in marked:
                            if cols[col].button(str(num), key=f"btn_{row}_{col}", use_container_width=True):
                                current_player_data['marked'].append(num)
                                current_player_data['history'].append(num)
                                st.rerun()
                
                st.markdown('</div>', unsafe_allow_html=True)
                
                # Undo button
                if st.button("↩️ Undo Last Mark"):
                    if current_player_data['history']:
                        last = current_player_data['history'].pop()
                        current_player_data['marked'].remove(last)
                        st.rerun()
                
                # Check wins
                new_wins = []
                
                # Check Jaldi 5
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
                
                for win in new_wins:
                    current_player_data['won_patterns'].append(win)
                    if win == "Full House":
                        st.success(f"🏆🏆🏆 CONGRATULATIONS! You won {win}! 🏆🏆🏆")
                        st.balloons()
                        # Add to chat
                        game['chat_messages'].append({
                            "player": "SYSTEM",
                            "message": f"🎉 {st.session_state.current_player} won {win}! 🎉",
                            "time": datetime.now()
                        })
                    else:
                        st.success(f"🎉 Congratulations! You won {win}! 🎉")
                        st.balloons()
                    
                    if new_wins:
                        st.rerun()
            
            elif current_player_data and current_player_data['is_winner']:
                st.success(f"🏆🏆🏆 WINNER! You won FULL HOUSE! 🏆🏆🏆")
                st.info("👀 You are now in spectator mode")
        
        with col_right:
            # Progress tracking
            st.markdown('<div class="section-header">📊 Game Progress</div>', unsafe_allow_html=True)
            
            show_progress = st.checkbox("Show numbers remaining", value=game['show_progress'])
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
                        st.success(f"🎯 Jaldi 5 (Row {row+1}): ✅")
                    else:
                        st.info(f"🎯 Jaldi 5 (Row {row+1}): {remaining} left")
                
                # Lines
                for line_num in range(3):
                    remaining = check_line(ticket, marked, line_num)
                    line_name = ["Top Line", "Middle Line", "Bottom Line"][line_num]
                    if remaining == 0:
                        st.success(f"📏 {line_name}: ✅")
                    else:
                        st.info(f"📏 {line_name}: {remaining} left")
                
                # Four corners
                remaining_corners = check_four_corners(ticket, marked)
                if remaining_corners == 0:
                    st.success(f"🔲 Four Corners: ✅")
                else:
                    st.info(f"🔲 Four Corners: {remaining_corners} left")
                
                # Full house
                remaining_fh = check_full_house(ticket, marked)
                if remaining_fh == 0:
                    st.success(f"🏆 Full House: ✅")
                else:
                    st.info(f"🏆 Full House: {remaining_fh} left")
                
                st.markdown('</div>', unsafe_allow_html=True)
            
            # Winners board
            st.markdown('<div class="section-header">🏆 Winners Board</div>', unsafe_allow_html=True)
            winners = [p for p in game['players'].values() if p.get('is_winner', False)]
            if winners:
                for i, winner in enumerate(winners[:4], 1):
                    st.markdown(f'<div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 10px; border-radius: 10px; margin: 5px 0; color: white; text-align: center;">🥇 Full House #{i}: {winner["name"]}</div>', unsafe_allow_html=True)
            else:
                st.info("No winners yet")
            
            # Call number button (host only)
            if st.session_state.is_host and game['game_started'] and not game['game_completed']:
                if st.button("🎲 CALL NEXT NUMBER", use_container_width=True, type="primary"):
                    if game['available_numbers']:
                        number = random.choice(game['available_numbers'])
                        game['available_numbers'].remove(number)
                        game['called_numbers'].append(number)
                        
                        # Get announcement
                        announcement = get_number_announcement(number)
                        game['last_announcement'] = announcement
                        
                        # Add to chat
                        game['chat_messages'].append({
                            "player": "🎤 ANNOUNCER",
                            "message": announcement,
                            "time": datetime.now()
                        })
                        
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
            
            # Computer auto-call
            if st.session_state.is_host and game['game_started'] and not game['game_completed']:
                computer_players = [p for p in game['players'].values() if p['name'].startswith('Computer')]
                if computer_players:
                    auto_call = st.checkbox("🤖 Auto-call numbers", value=False)
                    if auto_call and game['available_numbers']:
                        number = random.choice(game['available_numbers'])
                        game['available_numbers'].remove(number)
                        game['called_numbers'].append(number)
                        
                        announcement = get_number_announcement(number)
                        game['last_announcement'] = announcement
                        
                        game['chat_messages'].append({
                            "player": "🎤 ANNOUNCER",
                            "message": announcement,
                            "time": datetime.now()
                        })
                        
                        for player in game['players'].values():
                            if not player['is_winner']:
                                flat_ticket = [num for row in player['ticket'] for num in row]
                                if number in flat_ticket and number not in player['marked']:
                                    player['marked'].append(number)
                                    player['history'].append(number)
                        st.rerun()
        
        # Chat section
        st.markdown("---")
        st.markdown('<div class="section-header">💬 Chat Room</div>', unsafe_allow_html=True)
        
        col_chat_input, col_emoji = st.columns([3, 1])
        
        with col_chat_input:
            chat_input = st.text_input("Type your message:", key="chat_input")
        with col_emoji:
            emoji = st.selectbox("😊", ["", "😂", "🎉", "🔥", "👏", "😎", "🥳", "😮", "🎯", "🏆"])
        
        if st.button("📤 Send", use_container_width=True):
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
        
        # Display chat
        chat_container = st.container()
        with chat_container:
            for msg in game['chat_messages'][-30:]:
                if msg["player"] == "🎤 ANNOUNCER":
                    st.markdown(f'<div class="chat-message" style="background-color: #e8f5e9; border-left-color: #4caf50;"><strong>🎤 {msg["player"]}:</strong> {msg["message"]}</div>', unsafe_allow_html=True)
                elif msg["player"] == "SYSTEM":
                    st.markdown(f'<div class="chat-message" style="background-color: #fff3e0; border-left-color: #ff9800;"><strong>{msg["player"]}:</strong> {msg["message"]}</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="chat-message"><strong>{msg["player"]}:</strong> {msg["message"]}</div>', unsafe_allow_html=True)
        
        # New game button
        if st.session_state.is_host and (game['game_completed'] or len(game['called_numbers']) == 90):
            if st.button("🔄 Start New Game", use_container_width=True):
                game['game_started'] = False
                game['called_numbers'] = []
                game['available_numbers'] = list(range(1, 91))
                game['game_completed'] = False
                game['last_announcement'] = None
                game['chat_messages'] = []
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
    <p>🎤 Number announcements with fun Tambola calls!</p>
</div>
""", unsafe_allow_html=True)
