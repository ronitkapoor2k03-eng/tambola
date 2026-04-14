import streamlit as st
import pandas as pd
import random
import string
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="Tambola Game - Social Play",
    page_icon="🎮",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .stApp {
        background-color: #ffffff;
    }
    .ticket-cell {
        display: inline-block;
        width: 45px;
        height: 45px;
        margin: 3px;
        text-align: center;
        line-height: 45px;
        border-radius: 8px;
        font-weight: bold;
        cursor: pointer;
    }
    .number-unmarked {
        background-color: #f0f0f0;
        border: 2px solid #ddd;
        color: #333;
    }
    .number-marked {
        background-color: #28a745;
        border: 2px solid #28a745;
        color: white;
    }
    .called-number {
        display: inline-block;
        width: 50px;
        height: 50px;
        margin: 5px;
        text-align: center;
        line-height: 50px;
        border-radius: 50%;
        background-color: #007bff;
        color: white;
        font-weight: bold;
        font-size: 18px;
    }
    .winner-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 10px;
        border-radius: 10px;
        margin: 5px 0;
        color: white;
        text-align: center;
    }
    .chat-message {
        background-color: #f8f9fa;
        padding: 8px;
        margin: 5px 0;
        border-radius: 8px;
        border-left: 3px solid #007bff;
    }
    .disclaimer {
        background-color: #fff3cd;
        border-left: 4px solid #ffc107;
        padding: 10px;
        margin: 10px 0;
        border-radius: 5px;
        font-size: 12px;
    }
    .player-card {
        background-color: #e3f2fd;
        padding: 8px;
        margin: 5px 0;
        border-radius: 5px;
        border-left: 3px solid #2196f3;
    }
    .host-badge {
        background-color: #ff9800;
        color: white;
        padding: 2px 8px;
        border-radius: 12px;
        font-size: 11px;
        margin-left: 8px;
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
            'game_completed': False
        }
    if 'current_player' not in st.session_state:
        st.session_state.current_player = None
    if 'joined_room' not in st.session_state:
        st.session_state.joined_room = False
    if 'is_host' not in st.session_state:
        st.session_state.is_host = False

init_session()

# Helper functions
def generate_ticket():
    """Generate a random Tambola ticket"""
    ticket = [[0 for _ in range(9)] for _ in range(3)]
    
    for col in range(9):
        start = col * 10 + 1
        end = col * 10 + 10
        if col == 0:
            start, end = 1, 9
        elif col == 8:
            start, end = 81, 90
        
        numbers = list(range(start, end + 1))
        selected = sorted(random.sample(numbers, 3))
        
        rows = random.sample([0, 1, 2], 3)
        for i, row in enumerate(rows):
            ticket[row][col] = selected[i]
    
    for row in range(3):
        numbers_in_row = [x for x in ticket[row] if x != 0]
        while len(numbers_in_row) > 5:
            for col in range(9):
                if ticket[row][col] != 0 and len(numbers_in_row) > 5:
                    ticket[row][col] = 0
                    numbers_in_row = [x for x in ticket[row] if x != 0]
        
        while len(numbers_in_row) < 5:
            for col in range(9):
                if ticket[row][col] == 0:
                    col_count = sum(1 for r in range(3) if ticket[r][col] != 0)
                    if col_count < 3:
                        start = col * 10 + 1
                        end = col * 10 + 10
                        if col == 0:
                            start, end = 1, 9
                        elif col == 8:
                            start, end = 81, 90
                        
                        available = list(range(start, end + 1))
                        used = [ticket[r][col] for r in range(3) if ticket[r][col] != 0]
                        available = [n for n in available if n not in used]
                        
                        if available:
                            ticket[row][col] = random.choice(available)
                            numbers_in_row = [x for x in ticket[row] if x != 0]
                            break
    
    return ticket

def check_line(ticket, marked, line_num):
    line = ticket[line_num]
    numbers = [n for n in line if n != 0]
    remaining = len([n for n in numbers if n not in marked])
    return remaining

def check_full_house(ticket, marked):
    all_numbers = [n for row in ticket for n in row if n != 0]
    remaining = len([n for n in all_numbers if n not in marked])
    return remaining

# Title
st.title("🎮 Tambola Game - Social Play")
st.markdown("*Create a room, invite friends, and play together!*")

# Sidebar - Player name entry
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
        
        # Leave room button
        if st.button("🚪 Leave Room", use_container_width=True):
            if st.session_state.current_player in st.session_state.game_state['players']:
                del st.session_state.game_state['players'][st.session_state.current_player]
            
            # If host leaves, assign new host or reset
            if st.session_state.is_host and st.session_state.game_state['players']:
                new_host = list(st.session_state.game_state['players'].keys())[0]
                st.session_state.game_state['host'] = new_host
                st.session_state.is_host = (st.session_state.current_player == new_host)
            
            st.session_state.joined_room = False
            st.session_state.is_host = False
            st.rerun()
    
    st.markdown("---")
    st.markdown("### 📢 Legal")
    st.markdown("""
    <div class="disclaimer">
    ⚠️ Free-to-play social game.<br>
    No real money, betting, or gambling.
    </div>
    """, unsafe_allow_html=True)

# Main content
if not st.session_state.current_player:
    # Show welcome screen
    st.info("👋 Please enter your name in the sidebar to continue")
    
elif not st.session_state.joined_room:
    # Room creation/joining screen
    st.markdown("## 🎮 Join or Create a Game")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🏠 Create New Room")
        st.markdown("Create a room and become the host")
        if st.button("Create Room", use_container_width=True):
            room_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
            st.session_state.game_state = {
                'room_code': room_code,
                'host': st.session_state.current_player,
                'players': {},
                'game_started': False,
                'called_numbers': [],
                'available_numbers': list(range(1, 91)),
                'chat_messages': [],
                'game_completed': False
            }
            st.session_state.game_state['players'][st.session_state.current_player] = {
                'name': st.session_state.current_player,
                'ticket': generate_ticket(),
                'marked': [],
                'history': [],
                'is_winner': False,
                'won_patterns': []
            }
            st.session_state.joined_room = True
            st.session_state.is_host = True
            st.rerun()
    
    with col2:
        st.markdown("### 🔗 Join Existing Room")
        room_code_input = st.text_input("Enter Room Code:", max_chars=6).upper()
        
        if st.button("Join Room", use_container_width=True) and room_code_input:
            # For MVP, we'll simulate room joining
            # In real implementation, this would check against actual rooms
            st.session_state.game_state = {
                'room_code': room_code_input,
                'host': "Host",  # This would be fetched
                'players': {},
                'game_started': False,
                'called_numbers': [],
                'available_numbers': list(range(1, 91)),
                'chat_messages': [],
                'game_completed': False
            }
            st.session_state.game_state['players'][st.session_state.current_player] = {
                'name': st.session_state.current_player,
                'ticket': generate_ticket(),
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
    
    # Room info header
    col_info, col_players = st.columns([1, 1])
    
    with col_info:
        st.markdown(f"### 🎲 Room: **{game['room_code']}**")
        if game['game_started']:
            st.markdown("🟢 **Game in progress**")
        else:
            st.markdown("🟡 **Waiting for host to start**")
    
    with col_players:
        st.markdown("### 👥 Players in Room")
        for player_name in game['players'].keys():
            host_tag = " 👑" if player_name == game['host'] else ""
            st.markdown(f'<div class="player-card">🎮 {player_name}{host_tag}</div>', unsafe_allow_html=True)
        
        # Computer player option (only for host before game starts)
        if st.session_state.is_host and not game['game_started']:
            if st.button("🤖 Add Computer Player", use_container_width=True):
                comp_name = f"Computer_{len(game['players'])}"
                game['players'][comp_name] = {
                    'name': comp_name,
                    'ticket': generate_ticket(),
                    'marked': [],
                    'history': [],
                    'is_winner': False,
                    'won_patterns': []
                }
                st.rerun()
    
    # Start game button (only host)
    if st.session_state.is_host and not game['game_started']:
        if len(game['players']) >= 1:
            if st.button("🚀 START GAME", use_container_width=True, type="primary"):
                game['game_started'] = True
                st.rerun()
        else:
            st.warning("Need at least 1 player to start!")
    
    # Game play area (only if game started)
    if game['game_started']:
        st.markdown("---")
        
        col_game, col_info = st.columns([2, 1])
        
        with col_game:
            # Player's ticket
            if current_player_data and not current_player_data['is_winner']:
                st.markdown("### 🎟️ Your Ticket")
                st.markdown("*Click on numbers as they are called*")
                
                ticket = current_player_data['ticket']
                marked = current_player_data['marked']
                
                for row in range(3):
                    cols = st.columns(9)
                    for col in range(9):
                        num = ticket[row][col]
                        if num != 0:
                            is_marked = num in marked
                            
                            if cols[col].button(
                                str(num), 
                                key=f"{st.session_state.current_player}_{row}_{col}_{num}",
                                use_container_width=True,
                                disabled=is_marked
                            ):
                                if num not in current_player_data['marked']:
                                    current_player_data['marked'].append(num)
                                    current_player_data['history'].append(num)
                                    st.rerun()
                
                # Undo button
                if st.button("↩️ Undo Last Mark"):
                    if current_player_data['history']:
                        last = current_player_data['history'].pop()
                        current_player_data['marked'].remove(last)
                        st.rerun()
                
                # Check wins
                for line_num in range(3):
                    line_name = ["Top Line", "Middle Line", "Bottom Line"][line_num]
                    if line_name not in current_player_data['won_patterns']:
                        if check_line(ticket, current_player_data['marked'], line_num) == 0:
                            current_player_data['won_patterns'].append(line_name)
                            st.success(f"🎉 You won {line_name}! 🎉")
                            st.balloons()
                
                if "Full House" not in current_player_data['won_patterns']:
                    if check_full_house(ticket, current_player_data['marked']) == 0:
                        current_player_data['won_patterns'].append("Full House")
                        current_player_data['is_winner'] = True
                        st.success(f"🏆 CONGRATULATIONS! You won FULL HOUSE! 🏆")
                        st.balloons()
                        st.rerun()
            
            elif current_player_data and current_player_data['is_winner']:
                st.success(f"🏆 Congratulations! You won FULL HOUSE! 🏆")
                st.info("👀 You're now spectating")
            
            # Called numbers display
            st.markdown("### 📢 Called Numbers")
            if game['called_numbers']:
                called_html = ""
                for num in game['called_numbers'][-30:]:
                    called_html += f'<span class="called-number">{num}</span>'
                st.markdown(called_html, unsafe_allow_html=True)
            else:
                st.info("No numbers called yet")
        
        with col_info:
            # Progress tracking
            st.markdown("### 📊 Your Progress")
            if current_player_data and not current_player_data['is_winner']:
                ticket = current_player_data['ticket']
                marked = current_player_data['marked']
                
                for line_num in range(3):
                    remaining = check_line(ticket, marked, line_num)
                    line_name = ["📏 Top Line", "📏 Middle Line", "📏 Bottom Line"][line_num]
                    if remaining == 0:
                        st.success(f"{line_name}: ✅ COMPLETE!")
                    else:
                        st.info(f"{line_name}: {remaining} left")
                
                remaining_fh = check_full_house(ticket, marked)
                if remaining_fh == 0:
                    st.success(f"🏆 Full House: ✅ COMPLETE!")
                else:
                    st.info(f"🏆 Full House: {remaining_fh} left")
            
            # Winners board
            st.markdown("### 🏆 Winners")
            winners = [p for p in game['players'].values() if p.get('is_winner', False)]
            if winners:
                for i, winner in enumerate(winners[:4], 1):
                    st.markdown(f'<div class="winner-card">🥇 Full House #{i}: {winner["name"]}</div>', unsafe_allow_html=True)
            else:
                st.info("No winners yet")
            
            # Call number button (only host)
            if st.session_state.is_host and game['game_started'] and not game['game_completed']:
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
        
        # Chat section
        st.markdown("---")
        st.markdown("### 💬 Chat")
        
        chat_container = st.container()
        with chat_container:
            for msg in game['chat_messages'][-20:]:
                st.markdown(f'<div class="chat-message"><strong>{msg["player"]}:</strong> {msg["message"]}</div>', unsafe_allow_html=True)
        
        col_chat, col_emoji = st.columns([3, 1])
        with col_chat:
            chat_input = st.text_input("Type your message:", key="chat_input")
        with col_emoji:
            emoji = st.selectbox("Quick emoji:", ["", "😊", "😂", "🎉", "🔥", "👏", "😎", "🥳"])
        
        if st.button("Send Message", use_container_width=True):
            if chat_input or emoji:
                message = chat_input + " " + emoji if emoji else chat_input
                game['chat_messages'].append({
                    "player": st.session_state.current_player,
                    "message": message,
                    "time": datetime.now()
                })
                st.rerun()
        
        # Reset game button (only host)
        if st.session_state.is_host and game['game_completed']:
            if st.button("🔄 Start New Game", use_container_width=True):
                game['game_started'] = False
                game['called_numbers'] = []
                game['available_numbers'] = list(range(1, 91))
                game['game_completed'] = False
                for player in game['players'].values():
                    player['ticket'] = generate_ticket()
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
    <p>Free-to-play social Tambola game. No real money, betting, or gambling.</p>
</div>
""", unsafe_allow_html=True)
