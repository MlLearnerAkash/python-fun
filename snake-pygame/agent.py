import torch
import random
import numpy as np 
from game import SnakeGameAI, Direction, Point
from collections import deque



MAX_MEMORY= 100_000
BATCH_SIZE= 1000
LR= 0.001


class Agent:
    
    def __init__(self):
        self.n_game= 0
        self.epsilon= 0
        self.gamma= 0
        self.memory= deque(maxlen= MAX_MEMORY) #popleft()
        #TODO: model, trainer
        self.model =None
        self.trainer = None

        

    def get_state(self, game):
        head= game.snake[0]
        point_l= Point(head.x -20, head.y)
        point_r = Point(head.x +20, head.y)
        point_u = Point(head.x, head.y-20)
        point_d = Point(head.x, head.y+20)

        dir_l = game.direction == Direction.LEFT
        dir_r = game.direction == Direction.RIGHT
        dir_u = game.direction == Direction.UP
        dir_d = game.direction == Direction.DOWN


        state = [

            #Danger straight
            (dir_r and game.is_collision(point_r)) or
            (dir_l and game.is_collision(point_l)) or
            (dir_u and game.is_collision(point_u)) or
            (dir_d and game.is_collision(point_d)),

            #Danger right
            (dir_u and game.is_collision(point_r)) or
            (dir_d and game.is_collision(point_l)) or
            (dir_l and game.is_collision(point_u)) or
            (dir_r and game.is_collision(point_d)),

            #Danger is on left
            (dir_u and game.is_collision(point_l)) or
            (dir_d and game.is_collision(point_r)) or
            (dir_r and game.is_collision(point_u)) or
            (dir_l and game.is_collision(point_d)),

            #Move Direction
            dir_l,
            dir_r,
            dir_u,
            dir_d,

            #Food location

            game.food.x < game.head.x,
            game.food.x > game.head.x, 
            game.food.y < game.head.y,
            game.food.y > game.head.y

        ]

        return np.array(state, dtype= int)


    def remember(self, state, action, reaward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))
    
    def train_long_memory(self):
        if len(self.memory) > BATCH_SIZE:
            mini_sample= random.sample(self.memory, BATCH_SIZE)
        else:
            mini_sample=self.memory

        states, action, rewards, next_states, dones =zip(*mini_sample)
        self.trainer.train_step(states, actions, rewards, next_states, dones)
        
    
    def train_short_memory(self, state, action, reaward, next_state, done):
        self.trainer.train_step(state, action, reward, next_state, done)

    def get_action(self, state):
        #random moves: trade off between exploration and exploitation
        self.epsilon = 80 - self.n_game

        final_move =[0,0,0]

        if random.randint(0,200) < self.epsilon:
            move = random.randint(0,2)
            final_move[move] =1
        else:
            state0 = torch.tensor(state, dtype=torch.float)
            prediction = self.model.predict(state0)
            move= torch.argmax(prediction).item()
            final_move[move] =1

        return final_move

    def train(self):
        plot_scores= []
        plot_mean_scores= []
        total_score = 0
        record= 0
        agent= Agent()
        snake= SnakeGameAI()

        while True:
            # get old state
            state_old=agent.get_state(game)

            # get move
            final_move= agent.get_action(state_old)

            #perfoem the move
            reaward, done, score = game.ploay_step(final_move)

            state_new = agent.get_step(game)


            #train short memory
            agent.train_short_memory(state_old, final_move, reaward, state_new, done)

            #remember
            agent.remember(state_old, final_move, reaward, state_new, done)

            if done:
                #train long memory, plot result

                game.reset()
                agent.n_game +=1

                agent.train_long_memory()

                if score >record:
                    record = score
                    #agent.model.save()

                

                print("game", agent.n_game, "score", score, "Record:", record)






        

if __name__ =="__main__":
    train()


