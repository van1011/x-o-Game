import time
import socket
import threading
from tkinter import *
from tkinter import messagebox


#Setup
HOST = ''
PORT = 
FORMAT = "utf-8"

your_turn = False
you_started = False

your_details = {
    "name": "",
    "symbol": "X"
}

opponent_details = {
    "name": "",
    "symbol": "O",
}


#Connect player
def connect():
    global your_details
    name = enterName.get()
    if len(name) < 1:
        messagebox.showerror(title="Name", message="Enter your name")
    else:
        your_details["name"] = name
        print("Success entry:", name)
        connect_to_server(name)
        
#Connect to server
def connect_to_server(name):
    global client

    try:
        #Load new game page
        welcome.pack_forget()
        main.pack(side=TOP)
        
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((HOST,PORT))
        sentName = name.encode(FORMAT)
        client.send(sentName)
        #send name to server
        
        threading._start_new_thread(msg_from_server,(client," "))
        
    except Exception as e:
        print(e)
        messagebox.showerror(title="Connection error", message="Failed to connect")

        
#Click button to place move
def click(btn):
    global your_turn

    position = buttons.index(btn)
    
    if your_turn:
        if moveValid(position):
            btn['text'] = your_details["symbol"]
            symbol = your_details["symbol"]
            btn['fg'] = symbol_color[symbol]
            button_valid[position] = False
            positionSend = "$position$" + str(position)
            client.send(positionSend.encode(FORMAT))

            if checkWin() and your_turn:
                lbl_status.config(text = "Game over, you won!")
            else:
                your_turn = False
                lbl_status["text"] = "STATUS: " + opponent_details["name"] + "'s turn!"
      
        else:
            messagebox.showerror('Game','choose a valid box')

    else:
        lbl_status["text"] = "STATUS: Wait for your turn!"
        lbl_status.config(foreground="red")



def msg_from_server(sck,m):
    
    global your_details, opponent_details, your_turn, you_started
    
    while True:
        server_sent = sck.recv(4096)

        if not server_sent: break

        server_msg = server_sent.decode()
        print("RECEIVED", server_msg)
        
        if server_msg.startswith("Welcome"):
            if server_msg == "Welcome Player 1":
                break
                lbl_status["text"] = "Welcome " + your_details["name"] + "! Waiting for player 2"
            elif server_msg == "Welcome Player 2":
                break
                lbl_status["text"] = "Welcome " + your_details["name"] + "! Game will start soon"
                
        elif server_msg.startswith('$restart$'):
            restart()
            
        elif server_msg.startswith("opponent_name$"):
            temp = server_msg.replace("opponent_name$", "")
            temp = temp.replace("symbol", "")
            name_index = temp.find("$")
            symbol_index = temp.rfind("$")
            opponent_details["name"] = temp[0:name_index]
            your_details["symbol"] = temp[symbol_index:len(temp)]

            # set opponent symbol
            if your_details["symbol"] == "O":
                opponent_details["symbol"] = "X"
            else:
                opponent_details["symbol"] = "O"

            lbl_status["text"] = "STATUS: " + opponent_details["name"] + " is connected!"
            time.sleep(3)
            
            # is it your turn to play? hey! 'O' comes before 'X'
            if your_details["symbol"] == "O":
                lbl_status["text"] = "STATUS: Your turn!"
                your_turn = True
                you_started = True
            else:
                lbl_status["text"] = "STATUS: " + opponent_details["name"] + "'s turn!"
                your_turn = False
                you_started = False
                
        elif server_msg.startswith("$position$"):
            position = int(server_msg.replace("$position$", ""))
            # update board
            update_board(position)
            

            # Does this cordinate leads to a win or a draw
            if checkWin() and not your_turn:  # opponent win
                lbl_status['text'] = "Game over, " + opponent_details["name"] + ' won!'
  
            else:
                your_turn = True
                lbl_status["text"] = "STATUS: Your turn!"
                lbl_status.config(foreground="black")


#update board shown once opponent makes move
def update_board(position):
    symbol = opponent_details['symbol']
    btn = buttons[position]
    btn.config(text = symbol, fg = symbol_color[symbol])
    #btn['fg'] = symbol_color[symbol]
    button_valid[position] = False

    if position == 0:button_valid[1] = False
 
    elif position == boxes - 1:button_valid[boxes - 2] = False

    else:
        button_valid[position - 1] = False
        button_valid[position + 1] = False

 
#Check if move is valid
def moveValid(position):
    
    if not button_valid[position]:
        return False
    elif position == 0:button_valid[1] = False
 
    elif position == boxes - 1:button_valid[boxes - 2] = False

    else:
        button_valid[position - 1] = False
        button_valid[position + 1] = False

    return True
    
    
#Check if someone has won
def checkWin():
    
    if True in button_valid: #if there is still a valid spot left
        return False
    else:
        disable_buttons()
        return True
        

#Disable buttons when game ends
def disable_buttons():
    for btn in buttons:
        btn.config(state=DISABLED)

#Reset Game
def send_restart():
    client.send('$restart$'.encode(FORMAT))
    print("ENTERED")
    restart()

def restart():
    global your_turn, you_started, button_valid
    print("ENTERED 2")

    for btn in buttons:
        btn['text'] = ' '
        btn.config(state=NORMAL)

    button_valid = [True]*boxes
    
    time.sleep(3)

    if you_started:
        you_started = False
        your_turn = False
        lbl_status["text"] = "STATUS: " + opponent_details["name"] + "'s turn!"
    else:
        you_started = True
        your_turn = True
        lbl_status["text"] = "STATUS: Your turn!"

#Tkinter
root = Tk()
root.title = 'Game'

#Welcome page
welcome = Frame(root)
name = Label(welcome, text = "Name:")
name.pack(side = LEFT)
enterName = Entry(welcome)
enterName.pack(side=LEFT)
connect = Button(welcome, text="Connect", command= connect)
connect.pack(side=LEFT)
welcome.pack(side=TOP)

#Create board
main = Frame(root)
default_color = 'white'
boxes = 9
buttons = []
button_valid = [True]*boxes
symbol_color={'X':'blue','O':'red'}


for c in range(boxes):
    btn = Button(main, text = ' ', bg = default_color, height =3, width = 6)
    btn.grid(column = c, row = 0, sticky = N+S+E+W)
    btn['command'] = lambda btn = btn: click(btn)
    buttons.append(btn)

lbl_status = Label(main, text="Status: Game about to start", font="Helvetica 14 bold")
lbl_status.grid(row=1, column = 1, columnspan = 5)

restart_button = Button(main, text = 'Restart', font = "Helvetica 14 bold",command = send_restart)
restart_button.grid(row=1, column = boxes-1, columnspan = 2)

main.pack_forget()

root.mainloop()

