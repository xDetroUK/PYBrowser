import os

import chess
from PIL import ImageGrab, ImageTk
from PIL.Image import Image
import tkinter as tk
import pyautogui as pg



class chessCheat:
    def __init__(self,image_path=None):
        self.croploc = [[246.0, 170.0, 1011.0, 933.0]]
        self.CONFIDENCE = 0.8
        self.DETECTION_NOICE_THRESHOLD = 12
        self.PIECES_PATH = './chess/pieces/'
        size = self.croploc[0][3] - self.croploc[0][1]  # 895 works best so far
        self.image_path = image_path
        self.BOARD_SIZE = size  # 895 works best so far
        self.CELL_SIZE = int(self.BOARD_SIZE /8)
        self.BOARD_TOP_COORD = self.croploc[0][1]  # the cordinate of top corner from the screenshot taken
        self.BOARD_LEFT_COORD = self.croploc[0][0]  #
        # players
        self.WHITE = 0
        self.BLACK = 1  # currently the black side doesn't work with cheating function, displays wrong side of the board

        # side to move
        self.side_to_move = ''
        # square to coords
        self.square_to_coords = []

        self.xposition = self.BOARD_LEFT_COORD
        self.yposition = self.BOARD_TOP_COORD

        # array to convert board square indices to coordinates (black)
        self.get_square = [
            'a8', 'b8', 'c8', 'd8', 'e8', 'f8', 'g8', 'h8',
            'a7', 'b7', 'c7', 'd7', 'e7', 'f7', 'g7', 'h7',
            'a6', 'b6', 'c6', 'd6', 'e6', 'f6', 'g6', 'h6',
            'a5', 'b5', 'c5', 'd5', 'e5', 'f5', 'g5', 'h5',
            'a4', 'b4', 'c4', 'd4', 'e4', 'f4', 'g4', 'h4',
            'a3', 'b3', 'c3', 'd3', 'e3', 'f3', 'g3', 'h3',
            'a2', 'b2', 'c2', 'd2', 'e2', 'f2', 'g2', 'h2',
            'a1', 'b1', 'c1', 'd1', 'e1', 'f1', 'g1', 'h1'
        ]
        # map piece names to FEN chars
        self.piece_names = {
            'black_king': 'k',
            'black_queen': 'q',
            'black_rook': 'r',
            'black_bishop': 'b',
            'black_knight': 'n',
            'black_pawn': 'p',
            'white_knight': 'N',
            'white_pawn': 'P',
            'white_king': 'K',
            'white_queen': 'Q',
            'white_rook': 'R',
            'white_bishop': 'B'
        }
        self.coordinates = [
            [549.0, 2.0, 675.0, 132.0],  # Black King
            [415.0, 14.0, 539.0, 132.0],  # Black Queen
            [958.0, 13.0, 1086.0, 133.0],  # Black Rook
            [686.0, 7.0, 811.0, 136.0],  # Black Bishom
            [823.0, 7.0, 950.0, 136.0],  # Black Knight
            [416.0, 286.0, 539.0, 406.0],  # Black Pawn
            [821.0, 417.0, 949.0, 542.0],  # White Knight
            [414.0, 555.0, 541.0, 678.0],  # White Pawn
            [552.0, 963.0, 674.0, 1084.0],  # White King
            [420.0, 964.0, 542.0, 1083.0],  # White Queen
            [961.0, 961.0, 1084.0, 1084.0],  # White Rook
            [278.0, 963.0, 406.0, 1085.0],  # White Bishom
            [958.0, 963.0, 1081.0, 1083.0]]  # Full Screen

        x = self.BOARD_LEFT_COORD
        y = self.BOARD_TOP_COORD

        # loop over board rows

        for row in range(8):
            # loop over board columns
            for col in range(8):
                # init square
                square = row * 8 + col

                # associate square with square center coordinates
                self.square_to_coords.append((int(x + self.CELL_SIZE / 2), int(y + self.CELL_SIZE / 2)))

                # increment x coord by cell size
                x += self.CELL_SIZE

            # restore x coord, increment y coordinate by cell size
            x = self.xposition
            y += self.yposition
    def scanBoard(self):
        if self.image_path:
            scrShot = Image.open(self.image_path)
        else:
            scrShot = ImageGrab.grab()

        topx, topy, botx, boty = 0, 0, 0, 0

        def get_mouse_posn(event):
            global topy, topx
            topx, topy = event.x, event.y

        def update_sel_rect(event):
            global topy, topx, botx, boty
            botx, boty = event.x, event.y
            canvas.coords(rect_id, topx, topy, botx, boty)  # Update selection rect.

        def finalImage(event):
            self.croploc = (canvas.coords([rect_id]))

        try:
            window = tk.Tk()
            img = ImageTk.PhotoImage(scrShot)
            canvas = tk.Canvas(window, width=img.width(), height=img.height(),borderwidth=0, highlightthickness=0)
            canvas.pack(expand=True)
            canvas.img = img  # Keep reference in case this code is put into a function.
            canvas.create_image(0, 0, image=img, anchor=tk.NW)
            rect_id = canvas.create_rectangle(topx, topy, topx, topy, dash=(2, 2), fill='', outline='white')
            canvas.bind('<Button-1>', get_mouse_posn)  # blind to mouse left click
            canvas.bind('<B1-Motion>', update_sel_rect)  # detects the motion of the mouse
            canvas.bind("<ButtonRelease-1>", finalImage)  # if left button is released
            window.mainloop()
        except:
            pass
    def recognize_position(self):
        # piece locations
        self.piece_locations = {
            'black_king': [],
            'black_queen': [],
            'black_rook': [],
            'black_bishop': [],
            'black_knight': [],
            'black_pawn': [],
            'white_knight': [],
            'white_pawn': [],
            'white_king': [],
            'white_queen': [],
            'white_rook': [],
            'white_bishop': []
        }
        # # loop over piece names
        for piece in self.piece_names.keys():
            # store piece locations
            for location in pg.locateAllOnScreen(self.PIECES_PATH + piece + '.png', confidence=self.CONFIDENCE):
                # false detection flag
                noise = False

                # loop over matched pieces
                for position in self.piece_locations[piece]:
                    # noice detection
                    if abs(position.left - location.left) < self.DETECTION_NOICE_THRESHOLD and \
                            abs(position.top - location.top) < self.DETECTION_NOICE_THRESHOLD:
                        noise = True
                        break

                # skip noice detections
                if noise: continue

                # detect piece
                self.piece_locations[piece].append(location)
            #    print('detecting:', piece, location)
        # return piece locations

        return self.piece_locations
    def locations_to_fen(self, piece_locations):
        # FEN string
        fen = ''

        # board top left corner coords
        x = self.BOARD_LEFT_COORD
        y = self.BOARD_TOP_COORD

        # loop over board rows
        for row in range(8):
            # empty square counter
            empty = 0

            # loop over board columns
            for col in range(8):
                # init square
                square = row * 8 + col

                # piece detection
                is_piece = ()

                # loop over piece types
                for piece_type in piece_locations.keys():
                    # loop over pieces
                    for piece in piece_locations[piece_type]:
                        if abs(piece.left - x) < self.DETECTION_NOICE_THRESHOLD and \
                                abs(piece.top - y) < self.DETECTION_NOICE_THRESHOLD:
                            if empty:
                                fen += str(empty)
                                empty = 0

                            fen += self.piece_names[piece_type]
                            is_piece = (square, self.piece_names[piece_type])

                if not len(is_piece):
                    empty += 1

                # increment x coord by cell size
                x += self.CELL_SIZE

            if empty: fen += str(empty)
            if row < 7: fen += '/'

            # restore x coord, increment y coordinate by cell size
            x = self.BOARD_LEFT_COORD
            y += self.CELL_SIZE

        # add side to move to fen
        fen += ' ' + self.side_to_move

        # add placeholders (NO EN PASSANT AND CASTLING are static placeholders)
        fen += ' KQkq - 0 1'

        # return FEN string
        return fen

    def returnvalues(self):
        locatep = self.recognize_position()
        postofen = self.locations_to_fen(locatep)
        print(locatep,'\n',postofen)
        return postofen
    def setupimgs(self,imagepath):
        img = Image.open(imagepath)

        for piece_name, coordinates in zip(self.piece_names.keys(), self.coordinates):
            x1, y1, x2, y2 = coordinates
            print(piece_name)
            piece = img.crop((x1, y1, x2, y2))

            filename = os.path.join("chess/pieces/", f'{piece_name}.png')
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            piece.save(filename)

    def updateboard(self):
        try:
            fen = self.locations_to_fen(self.recognize_position())  # example FEN
            borard = chess.Board(fen=fen)
            print(borard)

        except Exception as e:
            print(f"Error updating the board: {str(e)}")
    def detect_screen_change(self,coordinates,active=''):
        previous_screenshot = None
        while active == "on":
            # Capture the screen at the specified coordinates
            screenshot = ImageGrab.grab(coordinates)

            # Compare the current screenshot with the previous one
            if previous_screenshot is not None and screenshot != previous_screenshot:
                return True

            # Update the previous screenshot
            previous_screenshot = screenshot

            # Pause for a short duration before taking the next screenshot
        return False

    def set_image_path(self, path):
        self.image_path = path