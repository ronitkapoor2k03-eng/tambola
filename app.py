import streamlit as st
import pandas as pd
import time
from datetime import datetime
from game_logic import TambolaGame, Player
from utils import generate_ticket, check_jaldi5, check_line, check_four_corners, check_full_house
import random
import string

# Page configuration
st.set_page_config(
    page_title="Tambola Game - Social Play",
    page_icon="🎮",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for light theme
st.markdown("""
<style>
    /* Light theme */
    .stApp {
        background-color: #ffffff;
    }
    
    /* Ticket styling */
    .ticket {
        background-color: #f8f9fa;
        padding: 15px;
        border-radius: 10px;
        border: 2px solid #dee2e6;
        margin: 10px 0;
    }
    
    .number-cell {
        display: inline-block;
        width: 40px;
        height: 40px;
        margin: 3px;
        text-align: center;
        line-height: 40px;
        border-radius: 5px;
        font-weight: bold;
        cursor: pointer;
    }
    
    .number-unmarked {
        background-color: #ffffff;
        border: 1px solid #dee2e6;
        color: #212529;
    }
    
    .number-marked {
        background-color: #28a745;
        border: 1px solid #28a745;
        color: white;
    }
    
    .called-number {
        display: inline-block;
        width: 45px;
        height: 45px;
        margin: 5px;
        text-align: center;
        line-height: 45px;
        border-radius: 50%;
        background-color: #007bff;
        color: white;
        font-weight: bold;
    }
    
    .winner-card {
        background: linear-gradient(135deg, #ffd89b 0%, #19547b 100%);
        padding: 10px;
        border-radius: 10px;
        margin: 5px 0;
        color: white;
    }
    
    /* Chat styling */
    .chat-message {
        background-color: #f8f9fa;
        padding: 10px;
        margin: 5px 0;
        border-radius: 10px;
        border-left: 4px solid #007bff;
    }
    
    .progress-box {
        background-color: #f8f9fa;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #dee2e6;
        margin: 10px 0;
    }
    
    /* Button styling */
    .stButton > button {
        background-color: #007bff;
        color: white;
        border: none;
        padding: 10px 20px;
        border-radius: 5px;
        font-weight: bold;
    }
    
    .stButton > button:hover {
        background-color: #0056b3;
    }
    
    /* Disclaimer */
    .disclaimer {
        background-color: #fff3cd;
        border-left: 4px solid #ffc107;
        padding: 10px;
        margin: 20px 0;
        border-radius: 5px;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
def init_session_state():
    if 'game' not in st.session_state:
        st.session_state.game = None
    if 'player_name' not in st.session_state:
        st.session_state.player_name = ""
    if 'room_code' not in st.session_state:
        st.session_state.room_code = None
    if 'joined' not in st.session_state:
        st.session_state.joined = False
    if 'chat_messages' not in st.session_state:
        st.session_state.chat_messages = []
    if 'show_progress' not in st.session_state:
        st.session_state.show_progress = True

init_session_state()

# Disclaimer
st.sidebar.markdown("""
<div class="disclaimer">
⚠️ <strong>Legal Disclaimer</strong><br>
This is a free-to-play social Tambola (Housie) game intended for entertainment only. 
No real money is involved, no betting, no gambling, and no rewards of monetary value.
</div>
""", unsafe_allow_html=True)

# Main title
st.title("🎮 Tambola Game - Social Play")
st.markdown("*Play with friends and family - No money involved, just pure fun!*")

# Sidebar for player info
with st.sidebar:
    st.markdown("### 👤 Player Info")
    
    if not st.session_state.joined:
        player_name = st.text_input("Enter your name:", value=st.session_state.player_name)
        if st.button("Join Game"):
            if player_name:
                st.session_state.player_name = player_name
                st.rerun()
            else:
                st.error("Please enter your name")
    else:
        st.success(f"Welcome, {st.session_state.player_name}!")
        
        if st.session_state.game and st.session_state.player_name in st.session_state.game.players:
            player = st.session_state.game.players[st.session_state.player_name]
            if player.is_winner:
                st.info("🏆 You are a winner! You're now spectating.")
    
    st.markdown("---")
    st.markdown("### 📢 About")
    st.info("""
    **How to Play:**
    1. Create or join a room
    2. Click numbers as they're called
    3. Win patterns like Jaldi 5, Lines, Corners, Full House
    4. Chat with other players!
    
    **MVP Version** - Built by Ronit Kapoor
    """)

# Main game area
col1, col2 = st.columns([2, 1])

with col1:
    # Room management
    if not st.session_state.joined:
        col_create, col_join = st.columns(2)
        
        with col_create:
            st.markdown("### 🏠 Create Room")
            if st.button("Create New Room", use_container_width=True):
                room_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
                game = TambolaGame(room_code)
                player = Player(st.session_state.player_name)
                game.add_player(st.session_state.player_name, player)
                st.session_state.game = game
                st.session_state.room_code = room_code
                st.session_state.joined = True
                st.rerun()
        
        with col_join:
            st.markdown("### 🔗 Join Room")
            room_code = st.text_input("Room Code:", max_chars=6).upper()
            if st.button("Join Room", use_container_width=True) and room_code:
                # In MVP, we'll simulate room joining
                game = TambolaGame(room_code)
                player = Player(st.session_state.player_name)
                game.add_player(st.session_state.player_name, player)
                st.session_state.game = game
                st.session_state.room_code = room_code
                st.session_state.joined = True
                st.rerun()
    
    else:
        # Game interface
        st.markdown(f"### 🎲 Room Code: **{st.session_state.room_code}**")
        
        game = st.session_state.game
        current_player = game.players.get(st.session_state.player_name)
        
        if game.game_started:
            # Display player's ticket
            if current_player and not current_player.is_winner:
                st.markdown("### 🎟️ Your Tambola Ticket")
                
                # Display ticket in grid format
                ticket_data = current_player.ticket
                
                # Create DataFrame for display
                df = pd.DataFrame(ticket_data)
                
                # Style the DataFrame
                def style_cells(val):
                    if val in current_player.marked_numbers:
                        return 'background-color: #28a745; color: white; font-weight: bold'
                    elif val != 0:
                        return 'background-color: #ffffff; border: 1px solid #dee2e6'
                    return 'background-color: #f8f9fa'
                
                styled_df = df.style.applymap(style_cells)
                st.dataframe(styled_df, use_container_width=True, height=200)
                
                # Undo button
                if st.button("↩️ Undo Last Mark"):
                    if current_player.marked_history:
                        last_mark = current_player.marked_history.pop()
                        current_player.marked_numbers.remove(last_mark)
                        st.rerun()
            elif current_player and current_player.is_winner:
                st.success(f"🏆 Congratulations! You won Full House! 🏆")
                st.info("👀 You're now in spectator mode")
            
            # Called numbers display
            st.markdown("### 📢 Called Numbers")
            called_numbers_html = ""
            for num in game.called_numbers:
                called_numbers_html += f'<span class="called-number">{num}</span>'
            st.markdown(called_numbers_html, unsafe_allow_html=True)
            
            # Full 1-90 board
            with st.expander("📊 Full Numbers Board (1-90)"):
                board_html = ""
                for i in range(1, 91):
                    if i in game.called_numbers:
                        board_html += f'<span class="called-number" style="background-color: #28a745;">{i}</span>'
                    else:
                        board_html += f'<span class="called-number" style="background-color: #6c757d;">{i}</span>'
                    if i % 10 == 0:
                        board_html += "<br>"
                st.markdown(board_html, unsafe_allow_html=True)
            
            # Game controls (only for host - first player)
            if st.session_state.player_name == list(game.players.keys())[0]:
                col_call, col_reset = st.columns(2)
                with col_call:
                    if st.button("🎲 Call Next Number", use_container_width=True):
                        if not game.game_completed:
                            number = game.call_number()
                            if number:
                                # Check winners
                                winners = game.check_all_winners()
                                if winners:
                                    for winner_name, pattern in winners:
                                        st.success(f"🎉 {winner_name} won {pattern}! 🎉")
                                        if pattern == "Full House":
                                            game.players[winner_name].is_winner = True
                                            if all(p.is_winner for p in game.players.values()):
                                                game.game_completed = True
                                                st.balloons()
                                                st.success("Game Over! All players have won!")
                                st.rerun()
                        else:
                            st.warning("Game is already completed!")
                
                with col_reset:
                    if st.button("🔄 Reset Game", use_container_width=True):
                        game.reset_game()
                        st.rerun()
            
            # Start game button
            if not game.game_started:
                if st.button("🚀 Start Game", use_container_width=True):
                    game.game_started = True
                    st.rerun()
        
        else:
            # Waiting room
            st.info("⏳ Waiting for host to start the game...")
            players_list = ", ".join(game.players.keys())
            st.markdown(f"**Players in room:** {players_list}")
            
            # Computer player option
            if len(game.players) == 1:
                if st.button("🤖 Play with Computer"):
                    computer = Player("Computer")
                    game.add_player("Computer", computer)
                    st.rerun()

with col2:
    # Progress box with toggle
    st.markdown("### 📊 Game Progress")
    
    toggle = st.checkbox("Show numbers remaining for patterns", value=st.session_state.show_progress)
    st.session_state.show_progress = toggle
    
    if st.session_state.show_progress and st.session_state.game and st.session_state.game.game_started:
        game = st.session_state.game
        current_player = game.players.get(st.session_state.player_name)
        
        if current_player and not current_player.is_winner:
            st.markdown('<div class="progress-box">', unsafe_allow_html=True)
            
            # Jaldi 5 progress
            remaining_j5 = check_jaldi5(current_player.ticket, current_player.marked_numbers)
            if remaining_j5:
                st.metric("🎯 Jaldi 5", f"{5 - len([m for m in current_player.marked_numbers if m in [num for row in current_player.ticket for num in row if num != 0][:5]])} numbers left")
            
            # Lines progress
            for line_num in range(3):
                remaining = check_line(current_player.ticket, current_player.marked_numbers, line_num)
                line_name = ["Top Line", "Middle Line", "Bottom Line"][line_num]
                if remaining is not None:
                    st.metric(f"📏 {line_name}", f"{remaining} numbers left")
            
            # Four corners
            remaining_corners = check_four_corners(current_player.ticket, current_player.marked_numbers)
            st.metric("🔲 Four Corners", f"{remaining_corners} corners left")
            
            # Full house
            remaining_fh = check_full_house(current_player.ticket, current_player.marked_numbers)
            st.metric("🏆 Full House", f"{remaining_fh} numbers left")
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    # Chat system
    st.markdown("### 💬 Chat")
    
    # Display chat messages
    chat_container = st.container()
    with chat_container:
        for msg in st.session_state.chat_messages[-20:]:
            st.markdown(f'<div class="chat-message"><strong>{msg["player"]}:</strong> {msg["message"]}</div>', unsafe_allow_html=True)
    
    # Chat input
    col_chat, col_emoji = st.columns([3, 1])
    with col_chat:
        chat_input = st.text_input("Type a message:", key="chat_input")
    with col_emoji:
        emojis = ["😊", "😂", "🎉", "🔥", "👏", "😎"]
        selected_emoji = st.selectbox("Quick emoji:", [""] + emojis)
    
    if st.button("Send Message", use_container_width=True):
        if chat_input or selected_emoji:
            message = chat_input + " " + selected_emoji if selected_emoji else chat_input
            st.session_state.chat_messages.append({
                "player": st.session_state.player_name,
                "message": message,
                "time": datetime.now()
            })
            st.rerun()
    
    # Winners board
    if st.session_state.game and st.session_state.game.game_started:
        st.markdown("### 🏆 Winners Board")
        winners = [p for p in st.session_state.game.players.values() if p.is_winner]
        if winners:
            for i, winner in enumerate(winners[:4], 1):
                st.markdown(f'<div class="winner-card">🥇 Full House #{i}: {winner.name}</div>', unsafe_allow_html=True)
        else:
            st.info("No winners yet!")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #6c757d; font-size: 12px;">
    <p>🎮 MVP (Minimum Viable Product) - Built by Ronit Kapoor</p>
    <p>This is a free-to-play social game. No real money, betting, or gambling involved.</p>
</div>
""", unsafe_allow_html=True)
