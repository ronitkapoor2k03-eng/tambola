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
        background-color: #f0f2f6;
    }
    
    /* House Board Styling - 10x9 grid */
    .house-board {
        background: white;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin: 10px 0;
    }
    
    .board-row {
        display: flex;
        justify-content: center;
        margin: 2px 0;
        flex-wrap: wrap;
    }
    
    .board-number {
        display: flex;
        align-items: center;
        justify-content: center;
        width: 65px;
        height: 55px;
        margin: 2px;
        text-align: center;
        border-radius: 8px;
        font-weight: bold;
        font-size: 14px;
        cursor: default;
        transition: all 0.2s;
    }
    
    /* Colors based on tens */
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
        background-color: #000000 !important;
        color: white !important;
        transform: scale(1.02);
    }
    
    /* Ticket Styling */
    .ticket-container {
        background: white;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin: 10px 0;
        overflow-x: auto;
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
    
    .computer-badge {
        background-color: #9b59b6;
        color: white;
        padding: 2px 10px;
        border-radius: 12px;
        font-size: 11px;
        margin-left: 8px;
    }
    
    .chat-message {
        background-color: #f8f9fa;
        padding: 8px 12px;
        margin: 8px 0;
        border-radius: 8px;
        border-left: 3px solid #007bff;
    }
    
    .progress-box {
        background: white;
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
        border: 1px solid #dee2e6;
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
    
    .computer-stats {
        background: linear-gradient(135deg, #9b59b6 0%, #8e44ad 100%);
        color: white;
        padding: 10px;
        border-radius: 8px;
        margin: 10px 0;
    }
    
    .live-players {
        background: #e3f2fd;
        padding: 10px;
        border-radius: 8px;
        margin: 10px 0;
        border-left: 4px solid #2196f3;
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
            'show_progress': True,
            'valid_rooms': {}
        }
    if 'current_player' not in st.session_state:
        st.session_state.current_player = None
    if 'joined_room' not in st.session_state:
        st.session_state.joined_room = False
    if 'is_host' not in st.session_state:
        st.session_state.is_host = False

init_session()

def generate_proper_ticket():
    """Generate a VALID Tambola ticket following all rules"""
    ticket = [[0 for _ in range(9)] for _ in range(3)]
    
    col_ranges = [
        list(range(1, 10)), list(range(10, 20)), list(range(20, 30)),
        list(range(30, 40)), list(range(40, 50)), list(range(50, 60)),
        list(range(60, 70)), list(range(70, 80)), list(range(80, 91))
    ]
    
    # Step 1: Decide how many numbers in each column (1-3 numbers per column)
    column_counts = []
    remaining = 15
    for col in range(9):
        if col == 8:
            count = remaining
        else:
            max_count = min(3, remaining - (8 - col))
            min_count = 1
            count = random.randint(min_count, max_count)
        column_counts.append(count)
        remaining -= count
    
    # Step 2: For each column, select random numbers and assign to rows
    for col in range(9):
        available_numbers = col_ranges[col].copy()
        selected_numbers = sorted(random.sample(available_numbers, column_counts[col]))
        rows = sorted(random.sample([0, 1, 2], column_counts[col]))
        
        for i, row in enumerate(rows):
            ticket[row][col] = selected_numbers[i]
    
    # Step 3: Ensure each row has exactly 5 numbers
    for row in range(3):
        current_count = len([ticket[row][col] for col in range(9) if ticket[row][col] != 0])
        
        if current_count > 5:
            filled_cols = [col for col in range(9) if ticket[row][col] != 0]
            to_remove = current_count - 5
            remove_cols = random.sample(filled_cols, to_remove)
            for col in remove_cols:
                ticket[row][col] = 0
        
        elif current_count < 5:
            empty_cols = [col for col in range(9) if ticket[row][col] == 0]
            needed = 5 - current_count
            
            valid_cols = []
            for col in empty_cols:
                col_count = len([ticket[r][col] for r in range(3) if ticket[r][col] != 0])
                if col_count < 3:
                    valid_cols.append(col)
            
            if len(valid_cols) >= needed:
                add_cols = random.sample(valid_cols, needed)
                for col in add_cols:
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
        
        sorted_pairs = sorted(zip(col_numbers, col_positions))
        
        for row in range(3):
            ticket[row][col] = 0
        
        for i, (num, row) in enumerate(sorted_pairs):
            ticket[row][col] = num
    
    return ticket

def get_number_color_class(num):
    tens = num // 10 if num < 90 else 9
    return f'num-{tens}'

def check_line(ticket, marked, line_num):
    line = ticket[line_num]
    numbers = [n for n in line if n != 0]
    return all(n in marked for n in numbers)

def check_four_corners(ticket, marked):
    corners = [ticket[0][0], ticket[0][8], ticket[2][0], ticket[2][8]]
    corners = [c for c in corners if c != 0]
    return all(c in marked for c in corners)

def check_full_house(ticket, marked):
    all_numbers = [n for row in ticket for n in row if n != 0]
    return all(n in marked for n in all_numbers)

def check_jaldi5(ticket, marked, last_called_number=None):
    """Check if player has 5 marked numbers (Jaldi 5)"""
    all_numbers = [n for row in ticket for n in row if n != 0]
    marked_numbers = [n for n in all_numbers if n in marked]
    
    if len(marked_numbers) == 5:
        if last_called_number:
            # Last number must match the called number
            return last_called_number in marked_numbers and marked_numbers[-1] == last_called_number
        return True
    return False

def verify_win(ticket, marked, win_type, last_called_number=None):
    if win_type == "Jaldi 5":
        return check_jaldi5(ticket, marked, last_called_number)
    elif win_type == "Top Line":
        return check_line(ticket, marked, 0)
    elif win_type == "Middle Line":
        return check_line(ticket, marked, 1)
    elif win_type == "Bottom Line":
        return check_line(ticket, marked, 2)
    elif win_type == "Four Corners":
        return check_four_corners(ticket, marked)
    elif win_type == "Full House":
        return check_full_house(ticket, marked)
    return False

def computer_claim_wins(player_name, player_data, game_state, last_called_number):
    """Computer automatically claims wins when achieved"""
    ticket = player_data['ticket']
    marked = player_data['marked']
    won_patterns = player_data['won_patterns']
    
    wins_to_claim = []
    
    # Check Jaldi 5 (first 5 numbers anywhere on ticket)
    if "Jaldi 5" not in won_patterns:
        if check_jaldi5(ticket, marked, last_called_number):
            wins_to_claim.append("Jaldi 5")
    
    # Check lines
    line_names = ["Top Line", "Middle Line", "Bottom Line"]
    for i, line_name in enumerate(line_names):
        if line_name not in won_patterns:
            if verify_win(ticket, marked, line_name):
                wins_to_claim.append(line_name)
    
    # Check four corners
    if "Four Corners" not in won_patterns:
        if verify_win(ticket, marked, "Four Corners"):
            wins_to_claim.append("Four Corners")
    
    # Check full house
    if "Full House" not in won_patterns:
        if verify_win(ticket, marked, "Full House"):
            wins_to_claim.append("Full House")
            player_data['is_winner'] = True
    
    for win in wins_to_claim:
        player_data['won_patterns'].append(win)
        game_state['chat_messages'].append({
            "player": "🤖 COMPUTER",
            "message": f"{player_name} won {win}! 🎉",
            "time": datetime.now()
        })
        if win == "Full House":
            game_state['chat_messages'].append({
                "player": "🤖 COMPUTER",
                "message": f"🏆🏆🏆 {player_name} won FULL HOUSE! 🏆🏆🏆",
                "time": datetime.now()
            })
    
    return len(wins_to_claim) > 0

# Title
st.title("🎮 Tambola (Housie) Game")
st.markdown("*Traditional Tambola with friends, family, or worldwide players!*")

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
        1. **Create room or play vs computer**
        2. **Click numbers on your ticket** (anytime!)
        3. **Claim wins** when you complete patterns
        4. **Wrong claim = Disqualification!**
        """)
    with col2:
        st.markdown("### 🏆 Winning Patterns")
        st.markdown("""
        • **Jaldi 5** - First 5 numbers anywhere
        • **Top/Middle/Bottom Line**
        • **Four Corners**
        • **Full House**
        """)
    with col3:
        st.markdown("### ⚠️ Important")
        st.markdown("""
        • **Jaldi 5 requires last number match!**
        • **Claim only if you actually won!**
        • **False claim = Disqualification**
        """)

elif not st.session_state.joined_room:
    st.markdown("## 🎮 Choose Your Game Mode")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 👥 Multiplayer Mode")
        st.markdown("Play with friends and family")
        
        col_create, col_join = st.columns(2)
        
        with col_create:
            if st.button("🏠 Create Room", use_container_width=True):
                room_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
                # Store the room in valid_rooms
                valid_rooms = st.session_state.game_state.get('valid_rooms', {})
                valid_rooms[room_code] = st.session_state.current_player
                
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
                    'valid_rooms': valid_rooms
                }
                st.session_state.game_state['players'][st.session_state.current_player] = {
                    'name': st.session_state.current_player,
                    'ticket': generate_proper_ticket(),
                    'marked': [],
                    'history': [],
                    'is_winner': False,
                    'is_disqualified': False,
                    'won_patterns': []
                }
                st.session_state.joined_room = True
                st.session_state.is_host = True
                st.rerun()
        
        with col_join:
            room_code_input = st.text_input("Enter Room Code:", max_chars=6).upper()
            if st.button("🔍 Join Room", use_container_width=True) and room_code_input:
                valid_rooms = st.session_state.game_state.get('valid_rooms', {})
                if room_code_input in valid_rooms:
                    st.session_state.game_state = {
                        'room_code': room_code_input,
                        'host': valid_rooms[room_code_input],
                        'players': {},
                        'game_started': False,
                        'called_numbers': [],
                        'available_numbers': list(range(1, 91)),
                        'chat_messages': [],
                        'game_completed': False,
                        'show_progress': True,
                        'valid_rooms': valid_rooms
                    }
                    st.session_state.game_state['players'][st.session_state.current_player] = {
                        'name': st.session_state.current_player,
                        'ticket': generate_proper_ticket(),
                        'marked': [],
                        'history': [],
                        'is_winner': False,
                        'is_disqualified': False,
                        'won_patterns': []
                    }
                    st.session_state.joined_room = True
                    st.session_state.is_host = False
                    st.rerun()
                else:
                    st.error("❌ Invalid Room Code! Please check and try again.")
    
    with col2:
        st.markdown("### 🌍 Worldwide Mode")
        st.markdown("Play against a random global player")
        
        if st.button("🎮 Find Random Opponent", use_container_width=True, type="primary"):
            room_code = "GLOBAL_" + ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
            computer_name = "Global_Player_" + ''.join(random.choices(string.digits, k=3))
            
            valid_rooms = st.session_state.game_state.get('valid_rooms', {})
            valid_rooms[room_code] = st.session_state.current_player
            
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
                'valid_rooms': valid_rooms
            }
            
            st.session_state.game_state['players'][st.session_state.current_player] = {
                'name': st.session_state.current_player,
                'ticket': generate_proper_ticket(),
                'marked': [],
                'history': [],
                'is_winner': False,
                'is_disqualified': False,
                'won_patterns': []
            }
            
            st.session_state.game_state['players'][computer_name] = {
                'name': computer_name,
                'ticket': generate_proper_ticket(),
                'marked': [],
                'history': [],
                'is_winner': False,
                'is_disqualified': False,
                'won_patterns': [],
                'is_computer': True
            }
            
            st.session_state.joined_room = True
            st.session_state.is_host = True
            st.rerun()

else:
    game = st.session_state.game_state
    current_player_data = game['players'].get(st.session_state.current_player)
    
    # Show room info
    st.markdown(f"## 🎲 Room: **{game['room_code']}**")
    
    # Live players list
    st.markdown("### 👥 Live Players in Room")
    st.markdown(f'<div class="live-players">🎮 <strong>{len(game["players"])} Player(s) connected</strong><br>', unsafe_allow_html=True)
    for player_name, player_data in game['players'].items():
        host_tag = " 👑 HOST" if player_name == game['host'] else ""
        winner_tag = " 🏆 WINNER" if player_data.get('is_winner', False) else ""
        computer_tag = " 🤖 AI" if player_data.get('is_computer', False) else ""
        disqualified_tag = " ❌ DQ" if player_data.get('is_disqualified', False) else ""
        st.markdown(f'• {player_name}{computer_tag}{host_tag}{winner_tag}{disqualified_tag}', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Computer stats
    computer_players = [p for p in game['players'].values() if p.get('is_computer', False)]
    if computer_players and game['game_started']:
        with st.expander("🤖 Opponent's Progress", expanded=True):
            for computer in computer_players:
                all_numbers = [n for row in computer['ticket'] for n in row if n != 0]
                marked_count = len(computer['marked'])
                st.markdown(f'<div class="computer-stats">🌍 <strong>{computer["name"]}</strong><br>✓ Numbers Marked: {marked_count}/15<br>🏆 Patterns Won: {len(computer["won_patterns"])}</div>', unsafe_allow_html=True)
    
    if current_player_data and current_player_data.get('is_winner', False):
        st.success(f"🏆🏆🏆 {st.session_state.current_player}, you are a WINNER! 🏆🏆🏆")
    elif current_player_data and current_player_data.get('is_disqualified', False):
        st.error(f"❌ {st.session_state.current_player}, you have been DISQUALIFIED for false claim!")
    
    # Host controls
    if not game['game_started']:
        if st.session_state.is_host and len(game['players']) >= 1:
            if st.button("🚀 START GAME", use_container_width=True, type="primary"):
                game['game_started'] = True
                st.rerun()
        elif not st.session_state.is_host:
            st.info(f"⏳ Waiting for host ({game['host']}) to start the game...")
    
    if game['game_started']:
        st.markdown("---")
        
        col_left, col_right = st.columns([2, 1])
        
        with col_left:
            # House Board - 10 rows x 9 columns (like real Tambola)
            st.markdown('<div class="section-header">🏠 TAMBOLA HOUSE BOARD</div>', unsafe_allow_html=True)
            st.markdown('<div class="house-board">', unsafe_allow_html=True)
            
            # Display 10 rows of 9 numbers each (1-90)
            for row in range(10):
                cols_html = '<div class="board-row">'
                for col in range(9):
                    num = row * 9 + col + 1
                    if num <= 90:
                        is_called = num in game['called_numbers']
                        color_class = get_number_color_class(num)
                        called_class = " called-number-board" if is_called else ""
                        cols_html += f'<div class="board-number {color_class}{called_class}">{num}</div>'
                cols_html += '</div>'
                st.markdown(cols_html, unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Called numbers list
            st.markdown('<div class="section-header">📢 Called Numbers</div>', unsafe_allow_html=True)
            if game['called_numbers']:
                recent_html = ""
                for num in game['called_numbers']:
                    color_class = get_number_color_class(num)
                    recent_html += f'<div class="board-number {color_class}" style="width: 50px; height: 50px; display: inline-flex; margin: 3px;">{num}</div>'
                st.markdown(recent_html, unsafe_allow_html=True)
            else:
                st.info("No numbers called yet. Host will call numbers!")
            
            # Player's Ticket - ALL NUMBERS CLICKABLE
            if current_player_data and not current_player_data.get('is_winner', False) and not current_player_data.get('is_disqualified', False):
                st.markdown('<div class="section-header">🎟️ YOUR TICKET</div>', unsafe_allow_html=True)
                st.markdown('<div class="ticket-container">', unsafe_allow_html=True)
                
                ticket = current_player_data['ticket']
                marked = current_player_data['marked']
                
                # Display ticket - ALL numbers clickable
                for row in range(3):
                    cols = st.columns(9)
                    for col in range(9):
                        num = ticket[row][col]
                        if num != 0:
                            if num in marked:
                                cols[col].markdown(f'<div style="background-color:#28a745; color:white; padding:15px; text-align:center; border-radius:8px; font-weight:bold;">✓ {num}</div>', unsafe_allow_html=True)
                            else:
                                # All numbers are clickable - player can mark any number
                                if cols[col].button(f"{num}", key=f"mark_{row}_{col}_{num}", use_container_width=True):
                                    current_player_data['marked'].append(num)
                                    current_player_data['history'].append(num)
                                    st.rerun()
                        else:
                            cols[col].markdown(f'<div style="background-color:#f8f9fa; padding:15px; text-align:center; border-radius:8px; color:#ccc;">-</div>', unsafe_allow_html=True)
                
                st.markdown('</div>', unsafe_allow_html=True)
                
                # Undo button
                col_undo, col_spacer = st.columns([1, 3])
                with col_undo:
                    if st.button("↩️ Undo Last Mark", use_container_width=True):
                        if current_player_data['history']:
                            last = current_player_data['history'].pop()
                            current_player_data['marked'].remove(last)
                            st.rerun()
                
                # Claim Win buttons
                st.markdown("---")
                st.markdown("### 🏆 Claim Your Win")
                st.warning("⚠️ Only claim if you actually achieved the pattern! False claims lead to disqualification!")
                
                col_claim1, col_claim2, col_claim3 = st.columns(3)
                
                with col_claim1:
                    # Jaldi 5 - First 5 numbers anywhere on ticket
                    if st.button("🎯 Claim Jaldi 5", use_container_width=True):
                        last_called = game['called_numbers'][-1] if game['called_numbers'] else None
                        if verify_win(ticket, marked, "Jaldi 5", last_called):
                            if "Jaldi 5" not in current_player_data['won_patterns']:
                                current_player_data['won_patterns'].append("Jaldi 5")
                                st.success("🎉 Valid claim! You won Jaldi 5!")
                                game['chat_messages'].append({
                                    "player": "🎉 SYSTEM",
                                    "message": f"{st.session_state.current_player} won Jaldi 5! 🎉",
                                    "time": datetime.now()
                                })
                                st.balloons()
                        else:
                            current_player_data['is_disqualified'] = True
                            st.error("❌ FALSE CLAIM! You have been DISQUALIFIED!")
                            game['chat_messages'].append({
                                "player": "⚠️ SYSTEM",
                                "message": f"{st.session_state.current_player} made a false claim and was DISQUALIFIED!",
                                "time": datetime.now()
                            })
                        st.rerun()
                    
                    if st.button("📏 Claim Top Line", use_container_width=True):
                        if verify_win(ticket, marked, "Top Line"):
                            if "Top Line" not in current_player_data['won_patterns']:
                                current_player_data['won_patterns'].append("Top Line")
                                st.success("🎉 Valid claim! You won Top Line!")
                                game['chat_messages'].append({
                                    "player": "🎉 SYSTEM",
                                    "message": f"{st.session_state.current_player} won Top Line! 🎉",
                                    "time": datetime.now()
                                })
                                st.balloons()
                        else:
                            current_player_data['is_disqualified'] = True
                            st.error("❌ FALSE CLAIM! You have been DISQUALIFIED!")
                            game['chat_messages'].append({
                                "player": "⚠️ SYSTEM",
                                "message": f"{st.session_state.current_player} made a false claim and was DISQUALIFIED!",
                                "time": datetime.now()
                            })
                        st.rerun()
                
                with col_claim2:
                    if st.button("📏 Claim Middle Line", use_container_width=True):
                        if verify_win(ticket, marked, "Middle Line"):
                            if "Middle Line" not in current_player_data['won_patterns']:
                                current_player_data['won_patterns'].append("Middle Line")
                                st.success("🎉 Valid claim! You won Middle Line!")
                                game['chat_messages'].append({
                                    "player": "🎉 SYSTEM",
                                    "message": f"{st.session_state.current_player} won Middle Line! 🎉",
                                    "time": datetime.now()
                                })
                                st.balloons()
                        else:
                            current_player_data['is_disqualified'] = True
                            st.error("❌ FALSE CLAIM! You have been DISQUALIFIED!")
                            game['chat_messages'].append({
                                "player": "⚠️ SYSTEM",
                                "message": f"{st.session_state.current_player} made a false claim and was DISQUALIFIED!",
                                "time": datetime.now()
                            })
                        st.rerun()
                    
                    if st.button("📏 Claim Bottom Line", use_container_width=True):
                        if verify_win(ticket, marked, "Bottom Line"):
                            if "Bottom Line" not in current_player_data['won_patterns']:
                                current_player_data['won_patterns'].append("Bottom Line")
                                st.success("🎉 Valid claim! You won Bottom Line!")
                                game['chat_messages'].append({
                                    "player": "🎉 SYSTEM",
                                    "message": f"{st.session_state.current_player} won Bottom Line! 🎉",
                                    "time": datetime.now()
                                })
                                st.balloons()
                        else:
                            current_player_data['is_disqualified'] = True
                            st.error("❌ FALSE CLAIM! You have been DISQUALIFIED!")
                            game['chat_messages'].append({
                                "player": "⚠️ SYSTEM",
                                "message": f"{st.session_state.current_player} made a false claim and was DISQUALIFIED!",
                                "time": datetime.now()
                            })
                        st.rerun()
                
                with col_claim3:
                    if st.button("🔲 Claim Four Corners", use_container_width=True):
                        if verify_win(ticket, marked, "Four Corners"):
                            if "Four Corners" not in current_player_data['won_patterns']:
                                current_player_data['won_patterns'].append("Four Corners")
                                st.success("🎉 Valid claim! You won Four Corners!")
                                game['chat_messages'].append({
                                    "player": "🎉 SYSTEM",
                                    "message": f"{st.session_state.current_player} won Four Corners! 🎉",
                                    "time": datetime.now()
                                })
                                st.balloons()
                        else:
                            current_player_data['is_disqualified'] = True
                            st.error("❌ FALSE CLAIM! You have been DISQUALIFIED!")
                            game['chat_messages'].append({
                                "player": "⚠️ SYSTEM",
                                "message": f"{st.session_state.current_player} made a false claim and was DISQUALIFIED!",
                                "time": datetime.now()
                            })
                        st.rerun()
                    
                    if st.button("🏆 Claim Full House", use_container_width=True):
                        if verify_win(ticket, marked, "Full House"):
                            if "Full House" not in current_player_data['won_patterns']:
                                current_player_data['won_patterns'].append("Full House")
                                current_player_data['is_winner'] = True
                                st.success("🏆🏆🏆 Valid claim! You won FULL HOUSE! 🏆🏆🏆")
                                game['chat_messages'].append({
                                    "player": "🎉 SYSTEM",
                                    "message": f"🏆🏆🏆 {st.session_state.current_player} won FULL HOUSE! 🏆🏆🏆",
                                    "time": datetime.now()
                                })
                                st.balloons()
                        else:
                            current_player_data['is_disqualified'] = True
                            st.error("❌ FALSE CLAIM! You have been DISQUALIFIED!")
                            game['chat_messages'].append({
                                "player": "⚠️ SYSTEM",
                                "message": f"{st.session_state.current_player} made a false claim and was DISQUALIFIED!",
                                "time": datetime.now()
                            })
                        st.rerun()
            
            elif current_player_data and current_player_data.get('is_winner', False):
                st.success(f"🏆🏆🏆 WINNER! You won FULL HOUSE! 🏆🏆🏆")
                st.info("👀 You are now in spectator mode")
            elif current_player_data and current_player_data.get('is_disqualified', False):
                st.error(f"❌ You have been DISQUALIFIED for making a false claim!")
                st.info("👀 You can only spectate now")
        
        with col_right:
            # Progress tracking
            st.markdown('<div class="section-header">📊 Your Progress</div>', unsafe_allow_html=True)
            
            if 'show_progress' not in game:
                game['show_progress'] = True
            show_progress = st.checkbox("Show numbers remaining", value=game['show_progress'])
            game['show_progress'] = show_progress
            
            if show_progress and current_player_data and not current_player_data.get('is_winner', False) and not current_player_data.get('is_disqualified', False):
                st.markdown('<div class="progress-box">', unsafe_allow_html=True)
                
                ticket = current_player_data['ticket']
                marked = current_player_data['marked']
                
                all_numbers = [n for row in ticket for n in row if n != 0]
                marked_count = len(marked)
                remaining = 15 - marked_count
                
                st.info(f"🎯 Total Numbers Marked: {marked_count}/15")
                
                if marked_count == 5:
                    st.success(f"🎯 Jaldi 5: ✅ READY TO CLAIM! (Last number must match called number)")
                else:
                    st.info(f"🎯 Jaldi 5: {5 - marked_count} more needed")
                
                # Lines
                for line_num in range(3):
                    is_complete = check_line(ticket, marked, line_num)
                    line_name = ["Top Line", "Middle Line", "Bottom Line"][line_num]
                    if is_complete:
                        st.success(f"📏 {line_name}: ✅ READY TO CLAIM!")
                    else:
                        remaining_line = len([n for n in ticket[line_num] if n != 0 and n not in marked])
                        st.info(f"📏 {line_name}: {remaining_line} more needed")
                
                # Four corners
                corners_complete = check_four_corners(ticket, marked)
                if corners_complete:
                    st.success(f"🔲 Four Corners: ✅ READY TO CLAIM!")
                else:
                    corners = [ticket[0][0], ticket[0][8], ticket[2][0], ticket[2][8]]
                    corners = [c for c in corners if c != 0]
                    remaining_corners = len([c for c in corners if c not in marked])
                    st.info(f"🔲 Four Corners: {remaining_corners} more needed")
                
                # Full house
                fh_complete = check_full_house(ticket, marked)
                if fh_complete:
                    st.success(f"🏆 Full House: ✅ READY TO CLAIM!")
                else:
                    st.info(f"🏆 Full House: {remaining} more needed")
                
                st.markdown('</div>', unsafe_allow_html=True)
            
            # Winners board
            st.markdown('<div class="section-header">🏆 Winners Board</div>', unsafe_allow_html=True)
            winners = [p for p in game['players'].values() if p.get('is_winner', False)]
            if winners:
                for i, winner in enumerate(winners[:4], 1):
                    st.markdown(f'<div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 10px; border-radius: 10px; margin: 5px 0; color: white; text-align: center;">🥇 Full House #{i}: {winner["name"]}</div>', unsafe_allow_html=True)
            else:
                st.info("No winners yet")
            
            # Disqualified players
            disqualified = [p for p in game['players'].values() if p.get('is_disqualified', False)]
            if disqualified:
                st.markdown("### ❌ Disqualified Players")
                for dq in disqualified:
                    st.markdown(f'<div style="background-color: #dc3545; color: white; padding: 5px; border-radius: 5px; margin: 2px 0; text-align: center;">{dq["name"]}</div>', unsafe_allow_html=True)
            
            # Call number button (host only)
            if st.session_state.is_host and game['game_started'] and not game['game_completed']:
                if st.button("🎲 CALL NEXT NUMBER", use_container_width=True, type="primary"):
                    if game['available_numbers']:
                        number = random.choice(game['available_numbers'])
                        game['available_numbers'].remove(number)
                        game['called_numbers'].append(number)
                        
                        game['chat_messages'].append({
                            "player": "🎲 HOST",
                            "message": f"Number called: {number}",
                            "time": datetime.now()
                        })
                        
                        # Computer auto-claims wins after each number
                        for player_name, player_data in game['players'].items():
                            if player_data.get('is_computer', False) and not player_data.get('is_winner', False) and not player_data.get('is_disqualified', False):
                                computer_claim_wins(player_name, player_data, game, number)
                        
                        st.rerun()
                    else:
                        st.warning("All numbers called!")
                        game['game_completed'] = True
        
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
                if "SYSTEM" in msg["player"]:
                    st.markdown(f'<div class="chat-message" style="background-color: #fff3e0; border-left-color: #ff9800;"><strong>{msg["player"]}:</strong> {msg["message"]}</div>', unsafe_allow_html=True)
                elif "COMPUTER" in msg["player"]:
                    st.markdown(f'<div class="chat-message" style="background-color: #f3e5f5; border-left-color: #9b59b6;"><strong>{msg["player"]}:</strong> {msg["message"]}</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="chat-message"><strong>{msg["player"]}:</strong> {msg["message"]}</div>', unsafe_allow_html=True)
        
        # New game button
        if st.session_state.is_host and (game['game_completed'] or len(game['called_numbers']) == 90):
            if st.button("🔄 Start New Game", use_container_width=True):
                game['game_started'] = False
                game['called_numbers'] = []
                game['available_numbers'] = list(range(1, 91))
                game['game_completed'] = False
                game['chat_messages'] = []
                for player in game['players'].values():
                    player['ticket'] = generate_proper_ticket()
                    player['marked'] = []
                    player['history'] = []
                    player['is_winner'] = False
                    player['is_disqualified'] = False
                    player['won_patterns'] = []
                st.rerun()

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; font-size: 12px;">
    <p>🎮 MVP (Minimum Viable Product) - Built by Ronit Kapoor</p>
    <p>Traditional Tambola (Housie) Game - Play with friends or worldwide players!</p>
    <p>✅ Click any number to mark | 🤖 Computer auto-claims wins | ❌ False claims = Disqualification</p>
</div>
""", unsafe_allow_html=True)
