import random
<<<<<<< HEAD
from gameView import init_Field, field_to_str, test_field_full, width, height
from gameLogic import validate_move, newFullField, game_over


# give random field and check if valid
class Game:
    rows, columns = init_Field()
    outstr = field_to_str(rows=rows, columns=columns)
    player1 = {"Name": "Player1", "Points": 0}
    player2 = {"Name": "Player2", "Points": 0}
    whose_turn = random.randint(0, 1)
    field_arrays = [rows, columns]

    def __init__(self):
        pass


    def calculate_active_player(self, whose_turn):

        if whose_turn == 0:
            return self.player1
        else:
            return self.player2

    def make_move(self, array_i, height, width):
        if validate_move(self.field_arrays, array_i, height, width) == True:
            self.field_arrays[array_i][height][width] = 1
            return True
        else:
            return False

    def random_move(self):
        success = False
        while not success and self.free_edge_count() > 0:
            w = random.randint(0, width + 1)
            h = random.randint(0, height + 1)
            i = random.randint(0, 2)
            success = self.make_move(i, h, w)

    def n_random_moves(self , n):
        for i in range(0,n):
            self.random_move()

    def convert_user_move_to_array(self, move):
        try:
            move = move.split(" ")
            move = list(map(int, move))
            if len(move) != 3:
                return False
            else:
                return move
        except:
            return False

    def free_edge_count(self):
        counter = 0
        for i in self.rows:
            for y in i:
                if y == 0:
                    counter+=1
                else:
                    continue
        for i in self.columns:
            for y in i:
                if y == 0:
                    counter+=1
                else:
                    continue
        return counter


    def obstacle_count(self):
        c = 0
        for h in range(height):
            for w in range(width):
                if test_field_full(self.field_arrays[0], self.field_arrays[1], h, w) == 1:
                    c += 1
        return c

    # print(print_Field(sefield_arrays[0], field_arrays[1]))

    # obstaclenumber = obstacle_count()
    #
    # # main loop
    # # make user and ai move TODO
    # # make random move TODO
    # while (not game_over(obstaclenumber, player1["Points"], player2["Points"])):
    #     active_player = calculate_active_player(whose_turn)
    #     move = input("{} make your move!".format(active_player["Name"]))
    #     move = convert_user_move_to_array(move)
    #     # then move invalid
    #     if move == False:
    #         print("move false")
    #         continue
    #
    #     if make_move(move[0], move[1], move[2]) == True:
    #         print("success")
    #         new_fields = newFullField(field_arrays, move[0], move[1], move[2])
    #         active_player["Points"] += new_fields
    #         if new_fields == 0:
    #             whose_turn = 1 - whose_turn
    #
    #     else:
    #         print("failed")
    #
    #     print(print_Field(field_arrays[0], field_arrays[1]))
    #     print(player1)
    #     print(player2)

game = Game()
while True and game.free_edge_count() > 0:
    print(field_to_str(game.rows, game.columns))
    print(game.free_edge_count())
    game.random_move()
print(field_to_str(game.rows, game.columns))
=======
from gameView import init_Field , print_Field , test_field_full , width , height
from gameLogic import validate_move , newFullField,game_over

rows, columns = init_Field()
outstr = print_Field(rows=rows, columns=columns)
player1 = {"Name": "Player1", "Points": 0}
player2 = {"Name": "Player2", "Points": 0}
whose_turn = random.randint(0, 1)
field_arrays = [rows, columns]

def calculate_active_player(whose_turn):
    if whose_turn == 0:
        return player1
    else:
        return player2


def make_move(array_i, height, width):
    if validate_move(field_arrays, array_i, height, width) == True:
        print("making move")
        field_arrays[array_i][height][width] = 1
        return True
    else:
        return False


def convert_user_move_to_array(move):
    try:
        move = move.split(" ")
        move = list(map(int, move))
        print(move)
        if len(move) != 3:
            return False
        else:
            return move
    except:
        return False

def obstacle_count():
    c = 0
    for h in range(height):
        for w in range(width):
            if test_field_full(field_arrays[0], field_arrays[1] , h , w) == 1 :
                c += 1
    return c



print(print_Field(field_arrays[0], field_arrays[1]))

obstaclenumber = obstacle_count()

# main loop
while (not game_over(obstaclenumber, player1["Points"], player2["Points"])):
    active_player = calculate_active_player(whose_turn)
    move = input("{} make your move!".format(active_player["Name"]))
    move = convert_user_move_to_array(move)
    # then move invalid
    if move == False:
        print("move false")
        continue

    if make_move(move[0], move[1], move[2]) == True:
        print("success")
        new_fields = newFullField(field_arrays, move[0], move[1], move[2])
        active_player["Points"] += new_fields
        if new_fields == 0:
            whose_turn = 1 - whose_turn

    else:
        print("failed")

    print(print_Field(field_arrays[0], field_arrays[1]))
    print(player1)
    print(player2)


>>>>>>> master
