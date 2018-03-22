import tensorflow
import numpy as np
import keras
from keras.models import Sequential
from keras.layers.core import Dense
from keras.optimizers import sgd
from gameLogic import *
from gamePlay import Game
import random
from gameView import width, height, field_to_str
from keras.models import load_model
import os.path

#global non_valid_move_reward
non_valid_move_reward = -10

class GameExtended(Game):
    def __init__(self):
        super().__init__()
        self.random_plays = 0

    def convert_action_to_move(self, action):
        array_i = 0
        w = 0
        h = 0
        for i in range(action):
            w += 1
            if w >= width + array_i:
                w = 0
                if array_i == 1:
                    h += 1
                array_i = 1 - array_i
        return array_i, h, w

    def convert_input_array_to_field(self, input):
        a = self.rows
        b = self.columns
        field = [a, b]
        for i in range(len(input)):
            array_i, h, w = self.convert_action_to_move(i)
            field[array_i][h][w] = input[i]
        return field

    def convert_field_to_inputarray(self, field):
        # field = [rows, colomns]
        input = np.zeros(40)
        index = 0
        for h in range(height + 1):
            # one for columns, one for rows
            for i in range(2):
                for w in range(width + 1):
                    # catch if too big
                    if i == 0 and w < len(field[0][0]):
                        if field[0][h][w] == 1:
                            input[index] = 1
                        index += 1
                    elif i == 1 and h < len(field[1]):
                        if field[1][h][w] == 1:
                            input[index] = 1
                        index += 1

        return input

    def convert_and_reshape_field_to_inputarray(self,field):
        input_array = self.convert_field_to_inputarray(field)
        r_input_array = input_array.reshape((1, -1))
        return r_input_array

    # action = move
    def _update_state(self, action, playernr):
        array_i, height, width = self.convert_action_to_move(action)
        old_field = [self.rows, self.columns]
        self.success = self.make_move(array_i, height, width)
        if not self.success:
            self.random_plays += 1
            array_i, height, width = self.random_move()
        new_fields = newFullField([self.rows, self.columns], array_i, height, width)
        self.calculate_active_player(playernr)["Points"] += new_fields

    def _get_reward(self, playernr, old_score):
        # return 1 if self.success else -1
        if not self.success:
            return non_valid_move_reward
        else:
            return self.get_player_score(playernr) - old_score

    def act(self, action, playernr):
        old_score = self.get_player_score(playernr)
        self._update_state(action, playernr)
        #reward = self._get_reward(playernr, old_score)
        gameover = game_over(self)
        return self.convert_and_reshape_field_to_inputarray([self.rows,self.columns]), old_score, gameover

    def random_act(self, playernr):
        success = False
        while not success and self.free_edge_count() > 0:
            action = random.randint(0, 40)
            array_i, h, w = self.convert_action_to_move(action)
            success = validate_move([self.rows, self.columns], array_i, h, w)
            if success:
                self._update_state(action, playernr)
                gameover = game_over(self)
                return self.convert_and_reshape_field_to_inputarray([self.rows,self.columns]), gameover


class Ai:
    def __init__(self, playernr, max_memory=100, discount=.9):
        self.playernr = playernr
        self.max_memory = max_memory
        self.memory = list()
        self.discount = discount

    def remember(self, states, gameover):
        self.memory.append([states, gameover])
        if len(self.memory) > self.max_memory:
            del self.memory[0]

    def get_batch(self, model, batch_size=10):
        len_memory = len(self.memory)
        num_actions = model.output_shape[-1]
        env_dim = self.memory[0][0][0].shape[1]
        inputs = np.zeros((min(len_memory, batch_size), env_dim))
        targets = np.zeros((inputs.shape[0], num_actions))

        for i, idx in enumerate(np.random.randint(0, len_memory, size=inputs.shape[0])):
            state_t, action_t, reward_t, state_next = self.memory[idx][0]
            gameover = self.memory[idx][1]
            inputs[i:i + 1] = state_t
            targets[i] = model.predict(state_t)[0]
            Q_sa = np.max(model.predict(state_next)[0])
            if gameover:
                targets[i, action_t] = reward_t
            else:
                targets[i, action_t] = reward_t + self.discount * Q_sa

        return inputs, targets



if __name__ == "__main__":

    epsilon = .1  # random moves
    num_actions = 40
    epoch = 25000
    max_memory = 500
    hidden_size = 200
    batch_size = 50
    model_name = "model_na{}_ep{}_mm{}_hs{}_nvr{}.h5".format(num_actions, epoch, max_memory, hidden_size,non_valid_move_reward)
    model_temp_name = "temp_" + model_name

    #     keras
    model = Sequential()

    model.add(Dense(hidden_size, input_shape=(40,), activation='relu'))
    model.add(Dense(hidden_size, activation='relu'))
    model.add(Dense(num_actions))  # output layer
    model.compile(optimizer=sgd(lr=.2), loss='mse')
    if os.path.isfile(model_name):
        model = load_model(model_name)

    testing_model = False

    if not testing_model:
        exp_replay = Ai(max_memory=max_memory, playernr=0)

        #     Train
        game_count = 0
        ai_wins = 0
        random_wins = 0
        ai_fields = 0
        random_fields = 0
        ai_played_random_count = 0
        for e in range(epoch):
            env = GameExtended()
            input = env.convert_and_reshape_field_to_inputarray([env.rows, env.columns])
            loss = 0.
            gameover = False
            predicted = False
            verbose = False
            old_score = False
            input_old = False
            action = False

            if verbose:
                print("starting game")
                print(field_to_str(env.rows, env.columns))
            while not gameover:
                #AIMOVE
                ai_should_play = True
                while ai_should_play and not gameover:
                    ai_should_play = False

                    playernr = 1
                    input_old = input
                    # sometimes  guessing is better than predicting
                    # get next action
                    if np.random.rand() <= epsilon:
                        action = random.randint(0, num_actions - 1)
                    else:
                        q = model.predict(input_old)
                        action = np.argmax(q[0])
                        game_count += 1
                        predicted = True
                    # apply action, get rewards and new state
                    old_points = env.player1["Points"]
                    input, old_score, gameover = env.act(action, playernr)
                    new_points = env.player1["Points"]
                    if new_points > old_points:
                        ai_should_play = True
                    if verbose:
                        print("AI PLAYED")
                        print(field_to_str(env.rows, env.columns))

                    if ai_should_play:
                        reward = env._get_reward(1, old_score)
                        # store experience
                        exp_replay.remember([input_old, action, reward, input], gameover)
                        # adapt model
                        inputs, targets = exp_replay.get_batch(model, batch_size=batch_size)
                        loss += model.train_on_batch(inputs, targets)

                # RANDOMMOVE
                random_should_play = True
                while not gameover and random_should_play:
                    random_should_play = False
                    playernr = 2
                    old_points = env.player2["Points"]
                    input, gameover = env.random_act(playernr)
                    new_points = env.player2["Points"]
                    if new_points > old_points:
                        random_should_play = True
                    if verbose:
                        print("Random PLAYED")
                        print(field_to_str(env.rows, env.columns))

                #after random has played AI can learn
                reward = env._get_reward(1, old_score)
                # store experience
                exp_replay.remember([input_old, action, reward, input], gameover)
                # adapt model
                inputs, targets = exp_replay.get_batch(model, batch_size=batch_size)
                loss += model.train_on_batch(inputs, targets)

            current_ai_field = env.player1["Points"]
            current_random_field = env.player2["Points"]
            if current_ai_field > current_random_field:
                ai_wins += 1
            elif current_random_field > current_ai_field:
                random_wins += 1
            ai_fields += current_ai_field
            random_fields += current_random_field
            ai_played_random_count += env.random_plays

            if (e % 100 == 0):
                model.save(model_temp_name,overwrite=True)
                print("Ai Wins: {}, with {} fields and {} random moves\n Random Wins: {} with {} fields".format(ai_wins, ai_fields, ai_played_random_count, random_wins, random_fields))
                ai_wins = 0
                ai_fields = 0
                random_fields = 0
                random_wins = 0
                ai_played_random_count = 0
                print("Epoch {:03d}/99999 | Loss {:.4f}".format(e, loss))

        model.save(model_name, overwrite=False)

    """
    else:
        model = load_model(model_name)
        env = GameExtended()
        success_count = 0
        for i in range(1000):

            env , input_array = env.create_train_data()
            field = env.convert_input_array_to_field(input_array.reshape(-1,1))
            print(field_to_str(field[0], field[1]))

            prediction = model.predict(input_array)
            action = np.argmax(prediction[0])

            env._update_state(action)

            print(env.convert_action_to_move(action))
            print(field_to_str(env.rows,env.columns))
            print(env.success)
            success_count += 1

        print("successcount: ", success_count)
    """
