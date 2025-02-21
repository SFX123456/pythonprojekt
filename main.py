import tkinter as tkin
from PIL import ImageTk,Image
import os.path
import chess
import chess.engine
from typing import List
from tkinter import filedialog, Toplevel
import chess.pgn

# to run install chess and pillow with pip and stockfish exe from here https://stockfishchess.org/download/
# drag the stockfish exe in the stockfish folder and rename the exe to stockfish
# https://theweekinchess.com/a-year-of-pgn-game-files go get pgn files to test // open game butto

stockfish_path = r"stockfish\stockfish.exe"  # Example for Windows
board = chess.Board()
engine = chess.engine.SimpleEngine.popen_uci(stockfish_path)
engine.configure({"UCI_ShowWDL": True})
print("Initial board:")
print(board)
moveNo = 0
playerGo = "It's white's move"
setMove = "w"
moves = {}

class Tile:
    def __init__(self, renderer: tkin.Canvas, name: str, index: int, orcolor: str, imageid: int):
        self.renderer: tkin.Canvas = renderer  # Type hint for renderer (Tkinter Canvas)
        self.name: str = name
        self.index: int = index
        self.imageid: int = imageid
        self.orcolor: str = orcolor

allTiles: List[Tile] = []
#master root and window
root = tkin.Tk()
root.title("Chess")
root.geometry("1300x1000")
script_dir = os.path.dirname(os.path.abspath(__file__))

dict = {}

def roundLabel():
    global moveNo
    roundText = tkin.Label(root,text="MOVE")
    roundNo = tkin.Label(root,text=(moveNo + 1))
    roundText.grid(column=0,row=9,sticky="w")
    roundNo.grid(column=0,row=9)
    roundText = tkin.Label(root,text="TURN")
    text = "white" if moveNo % 2 == 0 else "black"
    roundNo = tkin.Label(root,text=text)
    roundText.grid(column=0,row=10,sticky="w")
    roundNo.grid(column=0,row=10)

def showeval(score ):
    text = f"Current Position Evaluation: "
    roundText = tkin.Label(root, text="Eval")
    roundNo = tkin.Label(root, text= text)
    roundText.grid(column=0, row=6, sticky="w")


def addbuttonsgooneturnback():
    global board
    global moveNo
    def takeoneturnback():
        global moveNo
        board.pop()
        moveNo -= 1
        
        if moveNo % 2 == 1:
            # black move
            board.pop()
            moveNo -= 1
            
        makeBoardCanvas()
        deleteAllHandlersAndCursorFromTiles()
        piecescolor = getAllPiecesFromColor(setMove)
        addSelectHandlersToPieces(piecescolor)
        roundLabel()
    roundButton = tkin.Button(root, text="Undo last move", command=takeoneturnback)
    roundButton.grid(column=0, row=2, sticky="w")

def addbuttonsgooneturnforward():
    global board
    global moveNo
    def addlatestmoves():
        global moveNo
        if moves.get(moveNo) and moves.get(moveNo + 1):
            board.push(moves.get(moveNo))
            board.push(moves.get(moveNo + 1))
            moveNo += 2
        makeBoardCanvas()
        deleteAllHandlersAndCursorFromTiles()
        piecescolor = getAllPiecesFromColor(setMove)
        addSelectHandlersToPieces(piecescolor)
        roundLabel()
    roundButton = tkin.Button(root, text="redo move", command=addlatestmoves)
    roundButton.grid(column=0, row=3, sticky="w")
def show_popupopengame(root):
    # Create a new top-level window (popup)
    def selectfile():
        global moveNo
        global moves
        file_path = filedialog.askopenfilename(title="Select a file")

        if file_path is None:  # If the user selected a file
            print("No file selected")
            return None

        pgn = open(file_path)
        game = chess.pgn.read_game(pgn)
        board.reset()
        moveNo = 0
        moves = {}
        for move in game.mainline_moves():
            board.push(move)
            moves[moveNo] = move
            moveNo += 1
        makeBoardCanvas()
    roundButton = tkin.Button(root, text="open game", command=selectfile)
    roundButton.grid(column=0, row=5, sticky="w")

def show_popup(root):
    # Create a new top-level window (popup)
    popup = tkin.Toplevel(root)
    popup.title("You sure?")
    popup.geometry("200x100")

    # Add a label to the popup
    label = tkin.Label(popup, text="Wanna make the move?")
    label.pack(pady=20)

    # Variable to store the result
    result = tkin.StringVar()

    # Function to set the result and close the popup
    def on_yes():
        result.set(True)
        popup.destroy()

    def on_no():
        result.set(False)
        popup.destroy()

    # Add Yes and No buttons to the popup
    yes_button = tkin.Button(popup, text="Yes", command=on_yes)
    yes_button.pack(side="left", padx=20, pady=10)

    no_button = tkin.Button(popup, text="No", command=on_no)
    no_button.pack(side="right", padx=20, pady=10)

    # Wait until the popup is closed before continuing execution
    popup.wait_window()

    # Return the result
    return result.get()

def getrelative(before, after):
    return before / after
    
def showbestmoves():
    global board
    global moveNo
    global allTiles
    def showbestmoveshandle():
        info = engine.analyse(board, chess.engine.Limit(depth=20), multipv=5)
        colors = ["yellow", "cyan", "magenta", "green", "blue"]
        index = 0
        sameor = {}
        sameor2 = {}
        for  move in info:
            actualmove : chess.Move = move["pv"][0]
            piece1 = getPieceAtIndex(actualmove.from_square)
            piece2 = getPieceAtIndex(actualmove.to_square)
            if sameor.get(actualmove.from_square) is not None:
                if sameor2.get(actualmove.from_square) is not None:
                    piece1.renderer.config(highlightcolor=colors[index])
                else:
                    piece1.renderer.config(highlightbackground=colors[index])
            else:
                piece1.renderer.config(bg=colors[index])
            piece2.renderer.config(bg=colors[index])
            index += 1
            sameor[actualmove.from_square] = piece1
            
    roundButton = tkin.Button(root, text="Show best moves", command=showbestmoveshandle)
    roundButton.grid(column=0, row=7, sticky="w")
    
def labelTop():
    topLabels = ["A","B","C","D","E","F","G","H"]
    count=1
    for letter in topLabels:
        letter = tkin.Label(root,text=letter)
        letter.grid(column=count,row=0,sticky="S")
        count+=1

def labelSide():
    #putting numbers in labels at side of board
    sideLabels = []
    sideLabels+= range(8,0,-1)
    count=1
    for num in sideLabels:
        num = tkin.Label(root,text=num)
        num.grid(column=0,row=count,sticky="E")
        count+=1

def getAllPiecesFromColor(color: str) -> List[Tile]:
    filtered_pieces = []
    for tile in allTiles:
        # Check if the color is white and the piece is white (lowercase name)
        if color == "w" and tile.name.isupper():
            filtered_pieces.append(tile)
        # Check if the color is black and the piece is black (uppercase name)
        elif color == "b" and tile.name.islower():
            filtered_pieces.append(tile)

    return filtered_pieces

def deleteAllHandlersAndCursorFromTiles():
    for tile in allTiles:
        tile.renderer.bind("<Button-1>", do_nothing)
        tile.renderer.bind("<Button-3>", do_nothing)
        tile.renderer.config(cursor="no", bg=tile.orcolor, highlightcolor=tile.orcolor, highlightbackground=tile.orcolor)

def addSelectHandlersToPieces(pieces: List[Tile]):
    for tile in pieces:
        tile.renderer.bind("<Button-1>", getselectedHandler(tile))
        tile.renderer.config(cursor="hand2")

def getColorNameFromPiec(piece: Tile):
    if piece.name == "":
        raise Exception("piece needs to have a name")   
    return "w" if piece.name.isupper() else "b"

def getPieceAtIndex(index: int) -> Tile:
    global allTiles
    for i, allpiece in enumerate(allTiles):
        if allpiece.index == index:
            return allpiece
        
    return None

        
    
def handleallvalidtiles(startpiece: Tile):
    for tile in board.legal_moves:
        if tile.from_square == startpiece.index:
            piecetoaddcolor = getPieceAtIndex(tile.to_square)
            piecetoaddcolor.renderer.config(bg="purple")
            piecetoaddcolor.renderer.config(cursor="hand2")
            piecetoaddcolor.renderer.bind("<Button-1>", getselectedtomoveHandler( startpiece, piecetoaddcolor))
            
def isTheSameMove(move: chess.Move, move2: chess.Move) -> bool:
    return move.to_square == move2.to_square and move.from_square == move2.from_square


def doMoveUiChanges( frompiece: Tile, topiece: Tile):
    colorName = getColorNameFromPiec(frompiece)
    if colorName == "b":
        open = Image.open(os.path.join(script_dir, "mats/b" + frompiece.name + ".png"))
    else:
        open = Image.open(os.path.join(script_dir, "mats/" + frompiece.name + ".png"))
    image = ImageTk.PhotoImage(open)
    dict[topiece.index] = None
    dict[topiece.index] = image
    imageid = topiece.renderer.create_image(50, 50, image=image)
    topiece.imageid = imageid
    topiece.name = frompiece.name
    frompiece.imageid = -10
    dict[frompiece.index] = None

def getselectedtomoveHandler(frompiece: Tile,topiece: Tile):
    def handler(event):
        global egal
        global moveNo

        info = engine.analyse(board, chess.engine.Limit(depth=20), multipv=5)

        egal = dict
        for legal_move in board.legal_moves:
            if legal_move.from_square == frompiece.index and legal_move.to_square == topiece.index:
                if not any(filter(lambda movetockeck: isTheSameMove(movetockeck["pv"][0], legal_move), info)):
                    print("the computer would not recommend that move")
                    res = show_popup(root)
                    if res == "0":
                        frompiece.renderer.config(bg="red")
                        continue

                board.push(legal_move)
                moves[moveNo] = legal_move
                makeBoardCanvas()
                setUpNextRound()

    return handler

def resettoselectpiece(event):
    print("remove all handlers")
    deleteAllHandlersAndCursorFromTiles()
    piecessamecolor = getAllPiecesFromColor(setMove)
    addSelectHandlersToPieces(piecessamecolor)
    for tile in allTiles:
        tile.renderer.config(bg=tile.orcolor)

def drawwinningBar():
    info = engine.analyse(board, chess.engine.Limit(depth=20))
    score = info['score']
    showeval(score)
    relscore = score.relative.score()
    if relscore is None:
        return 
    relscore += 10000
    percentage = (relscore / 20000) * 100

    canvas = tkin.Canvas(root, width=50, height=1000)
    canvas.place(x=1250, y=0)  # Positioning the canvas on the right side
    bar_width = 50
    bar_height = 1000

    # Draw the full background of the bar (light gray)
    canvas.create_rectangle(0, 0, bar_width, bar_height, fill="brown")

    # Calculate how much of the bar should be filled
    red_height = bar_height * (percentage / 100)

    # Draw the red portion based on the percentage
    canvas.create_rectangle(0, bar_height - red_height, bar_width, bar_height, fill="white")
            
def getselectedHandler(piece: Tile):
    def handler(event):
        deleteAllHandlersAndCursorFromTiles()
        handleallvalidtiles(piece)

    return handler


def do_nothing(event):
    pass  # This function does nothing when an event is triggered


def makeBoardCanvas():
    global dict
    global board
    global allTiles
    for widget in root.winfo_children():
        widget.destroy()
    allTiles = []
    roundLabel()
    showbestmoves()
    drawwinningBar()
    addbuttonsgooneturnback()
    addbuttonsgooneturnforward()
    show_popupopengame(root)
    header = tkin.Label(root,text="2D Chess",)
    header.config(font=("courier",20))
    header.grid(column=0,row=0)
    labelTop()
    labelSide()
    dictallpieces = {}
    for square in chess.SQUARES:
        piece = board.piece_at(square)  # Get the piece at this square
        if piece:  # If there's a piece on the square
            rows = (square // 8)
            color = "brown" if (square + rows) % 2 == 0 else "white"
            if piece.symbol().isupper():
                open = Image.open(os.path.join(script_dir, "mats/" + piece.symbol() + ".png"))
            else:
                open = Image.open(os.path.join(script_dir, "mats/b" + piece.symbol() + ".png"))
            image = ImageTk.PhotoImage(open)
            dict[square] = image
            renderer = tkin.Canvas(root, width=110, height=110, border=0, bg=color, cursor="hand2", highlightthickness=3, highlightbackground=color)
            columns = square % 8 + 1
            renderer.grid(column= columns,row=(8 -rows))
            imageid = renderer.create_image(50, 50, image=image)
            tile = Tile(renderer, piece.symbol() , square, color, imageid)
            allTiles.append(tile)
            dictallpieces[square] = tile
            
    counterindex = 0
    for row in range(8):
        for index in range(8):
            if dictallpieces.get(counterindex) is None:
                color = "brown" if (index + row) % 2 == 0 else "white"
                renderer = tkin.Canvas(root, width=110, height=110, border=0, bg=color, cursor="no", highlightthickness=3, highlightbackground=color)
                renderer.grid(column= index + 1,row=(8 - row))
                tile = Tile(renderer, "", counterindex, color, -10)
                allTiles.append(tile)
            counterindex+= 1

    return allTiles

def aiturn():
    global engine
    global board
    result = engine.play(board, chess.engine.Limit(time=2))  # Let the engine think for 2 seconds
    board.push(result.move)
    moves[moveNo] = result.move
    print("ai is doing move " + str(result.move))
    makeBoardCanvas()

def ckeckforlose():
    if board.is_game_over() is False:
        return None
    
    popup = tkin.Tk()
    popup.geometry("300x50")
    message = ""
    if board.is_checkmate():
        message = ("Checkmate!")
    elif board.is_stalemate():
        message = ("Stalemate!")
    elif board.is_insufficient_material():
        message = ("Draw by insufficient material!")
    elif board.is_seventyfive_moves():
        message = ("Draw by 75-move rule!")
    elif board.is_fivefold_repetition():
        message = ("Draw by fivefold repetition!")
    elif board.is_variant_draw():
        message = ("Draw due to variant rules!")
    
    popup.wm_title(message)

    popup.mainloop()



#main
pieces = makeBoardCanvas()

root.bind("<Button-3>", resettoselectpiece)
moveNo = -1
def setUpNextRound():
    
    global moveNo
    global setMove
    global playerGo
    ckeckforlose()
    moveNo += 1
    if moveNo % 2 == 0:
        playerGo = "It's white's move"
        setMove = "w"
    else:
        playerGo = "It's black's move. Waiting for ai move"
        setMove = "b"
        aiturn()
        setUpNextRound()
        return
    deleteAllHandlersAndCursorFromTiles()
    piecescolor = getAllPiecesFromColor(setMove)
    addSelectHandlersToPieces(piecescolor)
    roundLabel()
    drawwinningBar()

setUpNextRound()

root.mainloop()
