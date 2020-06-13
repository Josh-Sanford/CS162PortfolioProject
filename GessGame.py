# Author: Josh Sanford
# Date: 6/4/2020
# Description: This file contains multiple classes that make up a game of Gess that can be played by two players.
#              The game continues until a player disrupts all of the opposite player's 'rings' or a player resigns.
#              For a detailed description of the game, follow the link provided in the readme.
# Note for the grader: I'm not passing the initial Gradescope test because my code depends on the choose_piece method
#                      in the GessGame class to create a piece which then acts as the current piece in the Board class.
#                      I believe when Gradescope tries to make a move, Board._current_piece is still None.


class GessGame:
    """
    Class to represent the game of Gess. This class uses composition with the Board and Player classes
    Responsibilities:
    Has a Board
    Has two players
    Knows state of the game
    Keeps up with whose turn it is
    Player can resign
    Player can make a move
    Collaborators:
    Board
    Player
    """

    def __init__(self):
        """
        Init method to initialize a game of Gess.
        Creates the board and the two players.
        Initializes the current_player, which starts as 'BLACK'.
        Initializes the game_state to 'UNFINISHED'.
        """
        self._board = Board()
        self.player_1 = Player('BLACK')  # black player
        self.player_2 = Player('WHITE')  # white player
        self._current_player = self.player_1
        self._opposing_player = self.player_2
        self._game_state = 'UNFINISHED'

    def get_board(self):
        """
        Getter method
        :return: the instance of the board
        """
        return self._board

    def get_current_player(self):
        """
        Getter method
        :return: the current player
        """
        return self._current_player

    def get_opposing_player(self):
        """
        Getter method
        :return: the opposing player
        """
        return self._opposing_player

    def set_game_state(self, game_state):
        """
        Setter method that sets the state of the game
        :param game_state: 'UNFINISHED', 'BLACK_WON', or 'WHITE_WON'
        :return:
        """
        self._game_state = game_state

    def get_game_state(self):
        """
        Returns the state of the game: 'UNFINISHED', 'BLACK_WON' or 'WHITE_WON'
        :return: current game_state
        """
        return self._game_state

    def resign_game(self, player):
        """
        Lets a player resign and forfeit the game
        :return: none
        """
        if player.get_team() == 'BLACK':
            self._game_state = 'WHITE_WON'
        if player.get_team() == 'WHITE':
            self._game_state = 'BLACK_WON'

    def make_move(self, current_location, new_location):
        """
        Initiates moving a piece to a new location
        Updates state of is_players_turn in Player class
        Updates number of rings the player has
        A piece must be chosen first
        :param current_location:
        :param new_location:
        :return: none
        """
        possible_moves = self._board.possible_moves(self._current_player)
        if new_location in possible_moves:
            current_location = current_location[0] + self._board.flip_numbers[current_location[1:]]
            new_location = new_location[0] + self._board.flip_numbers[new_location[1:]]
            self._board.move_piece(current_location, new_location, self._current_player, self._opposing_player)
            self.identify_rings(self._current_player)
            self.identify_rings(self._opposing_player)
            # split this logic up so the correct player wins
            if self._current_player.get_rings() == 0 or self._opposing_player.get_rings() == 0:
                team = self._current_player.get_team()
                self.set_game_state(team + "_WON")
                print(self.get_game_state())
            self.next_turn(self._current_player, self._opposing_player)
            return True
        else:
            return False

    def choose_piece(self, center_square):
        """
        A player can choose what "is" a piece each turn, and a piece can be any 3x3 grid of squares containing
        only the player's stones. Need to also consider a piece's footprint.
        :param center_square: coordinate chosen to be the center_square of the piece
        :return: True if it is a valid piece, False otherwise
        """
        center_square = center_square[0] + self._board.flip_numbers[center_square[1:]]
        if self._board.is_a_piece(center_square, self._current_player):
            self._board.make_piece(center_square)
            return True
        else:
            return False

    def next_turn(self, current_player, opposing_player):
        """
        Changes the current player to the next player
        :return: none
        """
        self._current_player = opposing_player
        self._opposing_player = current_player

    def identify_rings(self, player):
        """
        Finds all of the players current rings, and if a player's number of rings goes to zero then the game is
        notified so that the game state can change to show the other player won.
        :return: none
        algorithm: iterate through each square, check if the square is_a_piece
        if it is a piece, make a temporary Piece object
        check each direction of the piece to see if it is a ring
        """
        stone = player.get_stone()
        num_of_rings = 0
        is_a_ring = None
        for num in range(0, 20):
            for char in range(ord('b'), ord('t')):
                coordinate = chr(char) + str(num)
                if self._board.is_a_piece(coordinate, player):
                    self._board.make_piece(coordinate)
                    # check if center square is empty
                    if self._board.get_current_piece().get_center_square_value() == ' ':
                        # check every direction for a stone
                        for direction in self._board.get_current_piece().footprint_values:
                            if direction != 'center' and self._board.get_current_piece().footprint_values[direction] == stone:
                                is_a_ring = True
                            elif direction != 'center':
                                is_a_ring = False
                                break
                        if is_a_ring is True:
                            num_of_rings += 1
        player.set_rings(num_of_rings)


class Board:
    """
    Class to represent the game board
    Responsibilities:
    Create a game board
    Puts pieces on board and keeps up with them. 'w' for white stones and 'b' for black stones
    A piece is referred to by the coordinates of its central square.
    The piece g5 covers the squares f4, f5, f6, g4, g5, g6, h4, h5, h6.
    Keeps up with the current piece
    Calculates possible moves of a piece
    Can move a piece
    Prints out game board
    Collaborators:
    Piece
    """

    def __init__(self):
        """
        Init method to initialize a Board object. Creates the game board and dictionaries for converting letter
        coordinates to numbers and vice/versa, and converting board numbers to array indexes. Also initializes the
        current piece to None.
        """
        self.alpha_to_index = {}
        index = 0
        for i in range(ord('a'), ord('t') + 1):
            self.alpha_to_index[chr(i)] = index
            index += 1
        self.index_to_alpha = {}
        index = 0
        for i in range(ord('a'), ord('t') + 1):
            self.index_to_alpha[index] = chr(i)
            index += 1
        self.flip_numbers = {}
        num = 20
        for i in range(0, 21):
            self.flip_numbers[str(i)] = str(num)
            num -= 1
        self._gess_board = [[' ' for i in range(21)] for i in range(21)]
        row_2_4_17_and_19 = 'ceghijklmnpr'
        for letter in row_2_4_17_and_19:
            self._gess_board[1][self.alpha_to_index[letter]] = 'w'
            self._gess_board[3][self.alpha_to_index[letter]] = 'w'
            self._gess_board[16][self.alpha_to_index[letter]] = 'b'
            self._gess_board[18][self.alpha_to_index[letter]] = 'b'
        row_3_and_18 = 'bcdfhijkmoqrs'
        for letter in row_3_and_18:
            self._gess_board[2][self.alpha_to_index[letter]] = 'w'
            self._gess_board[17][self.alpha_to_index[letter]] = 'b'
        row_7_and_14 = 'cfilor'
        for letter in row_7_and_14:
            self._gess_board[6][self.alpha_to_index[letter]] = 'w'
            self._gess_board[13][self.alpha_to_index[letter]] = 'b'
        row_20 = 'abcdefghijklmnopqrst'
        for letter in row_20:
            self._gess_board[20][self.alpha_to_index[letter]] = letter
        for row in range(20):
            self._gess_board[row][20] = str(20 - row)

        self._current_piece = None
        self.out_of_bounds_columns = ['a', 't']
        self.out_of_bounds_rows = ['0', '19']

    def get_gess_board(self):
        """
        Getter method
        :return: the gess board in its current state
        """
        return self._gess_board

    def get_current_piece(self):
        """
        Getter method
        :return: the current piece on the board
        """
        return self._current_piece

    def update_board(self, coordinate, value):
        """
        Method to update the gess_board.
        :param coordinate:
        :return: none
        """
        column = self.alpha_to_index[coordinate[0]]
        row = int(coordinate[1:])

        if self.out_of_bounds(coordinate):
            self._gess_board[row][column] = ' '
        else:
            self._gess_board[row][column] = value

    def is_a_piece(self, center_square, current_player):
        """
        Checks to see if a given center_square can be a valid piece
        :param center_square: Coordinate of the center_square chosen for the piece
        :param current_player: the current player
        :return: boolean to tell whether it is a valid piece
        """
        try:
            north = self._gess_board[int(center_square[1:]) - 1][self.alpha_to_index[center_square[0]]]
            north_west = self._gess_board[int(center_square[1:]) - 1][self.alpha_to_index[center_square[0]] - 1]
            north_east = self._gess_board[int(center_square[1:]) - 1][self.alpha_to_index[center_square[0]] + 1]
            west = self._gess_board[int(center_square[1:])][self.alpha_to_index[center_square[0]] - 1]
            east = self._gess_board[int(center_square[1:])][self.alpha_to_index[center_square[0]] + 1]
            south = self._gess_board[int(center_square[1:]) + 1][self.alpha_to_index[center_square[0]]]
            south_west = self._gess_board[int(center_square[1:]) + 1][self.alpha_to_index[center_square[0]] - 1]
            south_east = self._gess_board[int(center_square[1:]) + 1][self.alpha_to_index[center_square[0]] + 1]
        except IndexError:
            return False
        footprint = [north, north_west, north_east, west, east, south, south_west, south_east]
        stone = current_player.get_stone()
        opposing_stone = current_player.get_opposing_stone()
        stones_in_piece = 0
        if self.out_of_bounds(center_square):
            return False
        for direction in footprint:
            if direction == opposing_stone:
                return False
            elif direction == stone:
                stones_in_piece += 1
        if stones_in_piece > 0:
            return True
        else:
            return False

    def out_of_bounds(self, coordinate):
        """
        Method checks if a square is out of bounds
        :param coordinate: square on the board that is being checked
        :return: True if the square is out of bounds, False otherwise.
        """
        if coordinate[0] in self.out_of_bounds_columns or coordinate[1:] in self.out_of_bounds_rows:
            return True
        else:
            return False

    def make_piece(self, center_square):
        """
        Creates a piece for the current turn
        :param center_square: coordinate of the center square of the piece
        :return: none
        """
        self._current_piece = Piece(center_square, self._gess_board, self.alpha_to_index, self.index_to_alpha)

    def hit_obstruction(self, coordinate, current_player):
        """
        Checks if an obstruction will be encountered, where an obstruction is a stone of either player
        :return: True if an obstruction is hit, False otherwise
        """
        temp_piece = Piece(coordinate, self._gess_board, self.alpha_to_index, self.index_to_alpha)
        for square in temp_piece.footprint_values:
            # if not part of current piece, check the square
            if temp_piece.footprint_coordinates[square] not in self._current_piece.footprint_coordinates.values():
                if temp_piece.footprint_values[square] == current_player.get_stone() or\
                        temp_piece.footprint_values[square] == current_player.get_opposing_stone():
                    return True
        return False

    def possible_moves(self, current_player):
        """
        Calculates the possible moves for the chosen piece
        :param current_player: the current player
        :return: list of coordinates for possible moves
        """
        stone = current_player.get_stone()
        opposing_stone = current_player.get_opposing_stone()
        possible_moves = []
        if self._current_piece.get_center_square_value() == stone:
            # piece can move as far as possible in any direction, but not including the center stone
            # movement is determined by stones not on center square
            for square in self._current_piece.footprint_values:
                if square != 'center' and self._current_piece.footprint_values[square] == stone:
                    for i in range(1, 20):
                        coordinate = self._current_piece.add_to_direction_coordinates(i, square)
                        if self.out_of_bounds(coordinate) is False:
                            coordinate = self._current_piece.add_to_direction_coordinates(i - 1, square)
                            # check each side for obstruction
                            if self.hit_obstruction(coordinate, current_player):
                                coordinate = coordinate[0] + self.flip_numbers[str(int(coordinate[1:]))]
                                possible_moves.append(coordinate)
                                break
                            else:
                                coordinate = coordinate[0] + self.flip_numbers[str(int(coordinate[1:]))]
                                possible_moves.append(coordinate)
                        else:
                            coordinate = self._current_piece.add_to_direction_coordinates(i - 1, square)
                            coordinate = coordinate[0] + self.flip_numbers[str(int(coordinate[1:]))]
                            possible_moves.append(coordinate)
                            break
        else:
            for square in self._current_piece.footprint_values: # returns keys which are strings 'north', etc.
                if square != 'center' and self._current_piece.footprint_values[square] == stone:
                    for i in range(1, 4):
                        coordinate = self._current_piece.add_to_direction_coordinates(i, square)
                        if self.out_of_bounds(coordinate) is False:
                            coordinate = self._current_piece.add_to_direction_coordinates(i - 1, square)
                            # check each side for obstruction
                            if self.hit_obstruction(coordinate, current_player):
                                coordinate = coordinate[0] + self.flip_numbers[str(int(coordinate[1:]))]
                                possible_moves.append(coordinate)
                                break
                            else:
                                coordinate = coordinate[0] + self.flip_numbers[str(int(coordinate[1:]))]
                                possible_moves.append(coordinate)
                        else:
                            coordinate = self._current_piece.add_to_direction_coordinates(i - 1, square)
                            coordinate = coordinate[0] + self.flip_numbers[str(int(coordinate[1:]))]
                            possible_moves.append(coordinate)
                            break
        return possible_moves

    def move_piece(self, current_location, new_location, current_player, opposing_player):
        """
        Moves the current chosen piece to a new location on the board
        :param current_location: square for the piece to be moved to
        :param new_location: Piece object to be moved
        :param current_player: The player who is making the move
        :param opposing_player: The opposite player
        :return: none
        """
        stone = current_player.get_stone()
        opposing_stone = current_player.get_opposing_stone()

        # piece is captured if in footprint
        old_piece = self._current_piece
        self.make_piece(new_location)
        new_piece = self._current_piece
        for square in new_piece.footprint_values:
            if new_piece.footprint_coordinates[square] not in old_piece.footprint_coordinates.values():
                if new_piece.footprint_values[square] == stone:
                    current_player.remove_stone()
            if new_piece.footprint_values[square] == opposing_stone:
                opposing_player.remove_stone()
            # add new piece to board
            self.update_board(new_piece.footprint_coordinates[square], old_piece.footprint_values[square])
            # delete old piece
            if old_piece.footprint_coordinates[square] not in new_piece.footprint_coordinates.values():
                self.update_board(old_piece.footprint_coordinates[square], ' ')

    def print_board(self):
        """
        Prints out the board in its current state
        :return: none
        """
        for b in range(len(self._gess_board)):
            print(self._gess_board[b])


class Piece:
    """
    Class to represent a piece on the board that is chosen by the player each turn
    Responsibilities:
    Has directions for the piece's footprint
    Is on the game board
    Collaborators:
    A board object is passed when the Piece is created
    """

    def __init__(self, center_square, board, alpha_to_index, index_to_alpha):
        """
        Init method to initialize a Piece object
        :param center_square: coordinate of the center square
        :param board: board object of the current game
        """
        self._board = board
        self._alpha_to_index = alpha_to_index
        self._index_to_alpha = index_to_alpha
        self._center_square = center_square
        self._center_square_value = self._board[int(center_square[1:])][alpha_to_index[center_square[0]]]
        self.footprint_coordinates = {  # column, row
            'center': self._center_square,
            'north': self._center_square[0] + str((int(self._center_square[1:]) - 1)),
            'north_west': self._index_to_alpha[self._alpha_to_index[self._center_square[0]] - 1] + str(
                (int(self._center_square[1:]) - 1)),
            'north_east': self._index_to_alpha[self._alpha_to_index[self._center_square[0]] + 1] + str(
                (int(self._center_square[1:]) - 1)),
            'west': self._index_to_alpha[self._alpha_to_index[self._center_square[0]] - 1] + self._center_square[1:],
            'east': self._index_to_alpha[self._alpha_to_index[self._center_square[0]] + 1] + self._center_square[1:],
            'south': self._center_square[0] + str((int(self._center_square[1:]) + 1)),
            'south_west': self._index_to_alpha[self._alpha_to_index[self._center_square[0]] - 1] + str(
                (int(self._center_square[1:]) + 1)),
            'south_east': self._index_to_alpha[self._alpha_to_index[self._center_square[0]] + 1] +
                          str((int(self._center_square[1:]) + 1)),
        }
        self.footprint_values = {  # row, column
            'center': self._center_square_value,
            'north': self._board[int(self._center_square[1:]) - 1][self._alpha_to_index[self._center_square[0]]],
            'north_west': self._board[int(self._center_square[1:]) - 1][
                self._alpha_to_index[self._center_square[0]] - 1],
            'north_east': self._board[int(self._center_square[1:]) - 1][
                self._alpha_to_index[self._center_square[0]] + 1],
            'west': self._board[int(self._center_square[1:])][self._alpha_to_index[self._center_square[0]] - 1],
            'east': self._board[int(self._center_square[1:])][self._alpha_to_index[self._center_square[0]] + 1],
            'south': self._board[int(self._center_square[1:]) + 1][self._alpha_to_index[self._center_square[0]]],
            'south_west': self._board[int(self._center_square[1:]) + 1][
                self._alpha_to_index[self._center_square[0]] - 1],
            'south_east': self._board[int(self._center_square[1:]) + 1][
                self._alpha_to_index[self._center_square[0]] + 1]
        }

    def get_center_square(self):
        """
        Getter method
        :return: coordinate of the center square of the Piece
        """
        return self._center_square

    def get_center_square_value(self):
        """
        Getter method
        :return: value at the center square of the Piece
        """
        return self._center_square_value

    def add_to_direction_coordinates(self, amount, direction):
        """
        Method add a given amount to the coordinates of the specified direction and returns the coordinates
        of that square
        :param amount: number to be added to the given direction
        :param direction: direction to be added in
        :return: the coordinate of the square being referenced
        """
        if direction == 'north':
            return self._center_square[0] + str((int(self._center_square[1:]) - 1 - amount))
        elif direction == 'north_west':
            return self._index_to_alpha[self._alpha_to_index[self._center_square[0]] - 1 - amount] + str(
                (int(self._center_square[1:]) - 1 - amount))
        elif direction == 'north_east':
            return self._index_to_alpha[self._alpha_to_index[self._center_square[0]] + 1 + amount] + str(
                (int(self._center_square[1:]) - 1 - amount))
        elif direction == 'west':
            return self._index_to_alpha[
                       self._alpha_to_index[self._center_square[0]] - 1 - amount] + self._center_square[1:]
        elif direction == 'east':
            return self._index_to_alpha[
                       self._alpha_to_index[self._center_square[0]] + 1 + amount] + self._center_square[1:]
        elif direction == 'south':
            return self._center_square[0] + str((int(self._center_square[1:]) + 1 + amount))
        elif direction == 'south_west':
            return self._index_to_alpha[self._alpha_to_index[self._center_square[0]] - 1 - amount] + str(
                (int(self._center_square[1:]) + 1 + amount))
        elif direction == 'south_east':
            return self._index_to_alpha[self._alpha_to_index[self._center_square[0]] + 1 + amount] + str(
                (int(self._center_square[1:]) + 1 + amount))
        else:
            print("Invalid direction")

    def add_to_direction_values(self, amount, direction):
        """
        Method adds a given amount to the coordinates of the specified direction and returns the value at that square
        :param amount: number to be added to the given direction
        :param direction: direction to be added in
        :return: the value at the square being referenced
        """
        if direction == 'north':
            return self._board[int(self._center_square[1:]) - 1 - amount][
                self._alpha_to_index[self._center_square[0]]]
        elif direction == 'north_west':
            return self._board[int(self._center_square[1:]) - 1 - amount][
                self._alpha_to_index[self._center_square[0]] - 1 - amount]
        elif direction == 'north_east':
            return self._board[int(self._center_square[1:]) - 1 - amount][
                self._alpha_to_index[self._center_square[0]] + 1 + amount]
        elif direction == 'west':
            return self._board[int(self._center_square[1:])][
                self._alpha_to_index[self._center_square[0]] - 1 - amount]
        elif direction == 'east':
            return self._board[int(self._center_square[1:])][
                self._alpha_to_index[self._center_square[0]] + 1 + amount]
        elif direction == 'south':
            return self._board[int(self._center_square[1:]) + 1 + amount][
                self._alpha_to_index[self._center_square[0]]]
        elif direction == 'south_west':
            return self._board[int(self._center_square[1:]) + 1 + amount][
                self._alpha_to_index[self._center_square[0]] - 1 - amount]
        elif direction == 'south_east':
            return self._board[int(self._center_square[1:]) + 1 + amount][
                self._alpha_to_index[self._center_square[0]] + 1 + amount]
        else:
            print("Invalid direction")


class Player:
    """
    Class to represent a player of the game
    Responsibilities:
    Has a count of remaining stones
    Has a count of the rings the player has
    Knows if it is the player's turn
    Has the team the player is on
    Removes stones when a stone is captured by the opponent
    Collaborators:
    none
    """

    def __init__(self, team):
        """
        Init method to initialize a Player object.
        :param team: color of the player's team
        """
        self._team = team  # black or white
        if self._team == 'BLACK':
            self._stone = 'b'
            self._opposing_stone = 'w'
        if self._team == 'WHITE':
            self._stone = 'w'
            self._opposing_stone = 'b'
        self._remaining_stones = 43
        self._rings = 1

    def get_team(self):
        """
        Gets the team of the player
        :return: string showing player's team
        """
        return self._team

    def get_stone(self):
        return self._stone

    def get_opposing_stone(self):
        return self._opposing_stone

    def get_remaining_stones(self):
        return self._remaining_stones

    def set_rings(self, num_of_rings):
        self._rings = num_of_rings

    def get_rings(self):
        return self._rings

    def remove_stone(self):
        """
        Decrements remaining_stones when a stone is captured
        :return: none
        """
        self._remaining_stones -= 1


def main():
    """
    Main method runs the game, getting user input and calling appropriate methods. The game continues as long as the
    game state is 'UNFINISHED.'
    :return: none
    """
    gess_game = GessGame()
    while gess_game.get_game_state() == 'UNFINISHED':
        current_player = gess_game.get_current_player()
        opposing_player = gess_game.get_opposing_player()
        gess_game.get_board().print_board()
        print(current_player.get_team(), "stones: ", current_player.get_remaining_stones())
        print(opposing_player.get_team(), "stones: ", opposing_player.get_remaining_stones())
        current_square = input(current_player.get_team() + " choose a piece or type 'quit' to resign: ")
        if current_square == 'quit':
            gess_game.resign_game(current_player)
            print(gess_game.get_game_state())
            break
        while gess_game.choose_piece(current_square) is False: # calls is_a_piece, which calls make_piece if True
            print("That is not a valid piece. Please try again.")
            current_square = input(current_player.get_team() + " choose a piece: ")
        possible_moves = gess_game.get_board().possible_moves(current_player)
        print("Possible moves: ", possible_moves)
        move = input("Please choose where to move your piece: ")
        while move not in possible_moves:
            print("Not a valid move. Please try again.")
            print("Possible moves: ", possible_moves)
            move = input("Please choose where to move your piece: ")
        gess_game.make_move(current_square, move)


if __name__ == '__main__':
    main()
