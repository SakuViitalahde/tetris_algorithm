import pygame
from GameState import GameState
from Blocks import Blocks
import copy
import time
import random

WIN_WIDTH = 700
WIN_HEIGHT = 645

def main(weights):
    running = True
    win = pygame.display.set_mode((WIN_WIDTH,WIN_HEIGHT))
    clock = pygame.time.Clock()
    game_state = GameState()
    blocks = Blocks()
    current_block = blocks.get_random_block()
    next_block = blocks.get_random_block()
    blocks_used = 0
    score = 0

    while running:
        clock.tick(300)

        # Next Block
        if not next_block:
            next_block = blocks.get_random_block()

        if not current_block.dropped:
            rotate, move = find_best_move(game_state, current_block, next_block, weights, blocks_used)
            for x in range(rotate):
                current_block.rotate_block(game_state)
            if move == 0:
                #Stay
                pass
            elif move < 0:
                for move in range(abs(move)):
                    current_block.move_left(game_state)
            elif move > 0:
                for move in range(move):
                    current_block.move_right(game_state)
            current_block.dropped = True
        
        game_state.draw_window(win, current_block, score, next_block)
        
        # Move Block
        if not current_block.move_down(game_state):
            game_state.game_state = game_state.set_current_block_to_gamestate(current_block)
            calculate_fitness(game_state, weights, blocks_used)
            current_block = next_block
            next_block = None
            score += 1
            blocks_used += 1
            score = game_state.check_tetris(score)

        if game_state.check_fail():
            pygame.quit()
            return score
        
        pygame.event.pump()

def main_loop():
    # To get this next level, should make population and random weights
    # Simulate 10 game each and pick best one. Mutate from that and make new copies.
    # run simulations again.
    # this way its easy to find best weights
    start_weights =  [-1.0, 0.5, -1.0, -1.0, -1.0, -1.0]
    top_score = 0
    population = []
    top_weights = None

    while top_score < 500:
        print("Generation Go:")
        population = []
        if not top_weights:
            population.append(start_weights)
            for x in range(50):
                new_weights = []
                for weight in start_weights:
                    new_weights.append(weight + random.uniform(-0.5,0.5))
                population.append(new_weights)
        else:
            for x in range(50):
                new_weights = []
                population.append(top_weights)
                for weight in top_weights:
                    new_weights.append(weight + random.uniform(-0.25,0.25))
                population.append(new_weights)

        scores = {}
        for idx, weight in enumerate(population):
            run_score = 0 
            for runi in range(10):
                run_score += main(weight)
            scores[idx] = run_score / 10
            if scores[idx] > top_score:
                top_weights = weight
                top_score = scores[idx]
                print(scores[idx])
                print(weight)
    print(scores)
    print(population)


def find_best_move(game_state, current_block, next_block, weights, blocks_used):
    best_fitness = -1000
    best_move = (0,0)
    rotates = 2

    # only make 4 rotates if T J L
    if current_block.shape == "T" or current_block.shape == "L" or current_block.shape == "J":
        rotates = 4

    # Loop rotates
    for rotate in range(rotates):
        game_state_copy = copy.deepcopy(game_state)
        current_block_copy = copy.deepcopy(current_block)

        # Rotate block
        for _ in range(rotate):
            current_block_copy.rotate_block(game_state_copy)
        positions = []

        # Loop Moves
        for move in range(-5,6):
            simulation_block = copy.deepcopy(current_block_copy)
            simulation_game_state = copy.deepcopy(game_state_copy)
            if move == 0:
                #Stay
                pass
            elif move < 0:
                # Move left
                for _ in range(move,0):
                    if not simulation_block.move_left(simulation_game_state):
                        break
            elif move > 0:
                # Move right
                for _ in range(move):
                    if not simulation_block.move_right(simulation_game_state):
                        break


            # Save positions so we dont calculate them again
            if simulation_block.block_position in positions:
                continue
            else:
                positions.append(simulation_block.block_position)

            # Calulate fitness value of first block
            simulation_game_state = drop_to_end(simulation_game_state,simulation_block)
            fitness = calculate_fitness(simulation_game_state, weights, blocks_used)

            ####
            #Future Block calculation
            ####

            # only make 4 rotates if T J L

            """
            rotates_next = 2
            if next_block.shape == "T" or next_block.shape == "L" or next_block.shape == "J":
                rotates_next = 4
                
            for rotate_next in range(rotates_next):
                game_state_copy_next = copy.deepcopy(simulation_game_state)
                next_block_copy = copy.deepcopy(next_block)
                
                # Rotate block
                for _ in range(rotate_next):
                    next_block_copy.rotate_block(game_state_copy_next)
                
                positions_next = []
                
                # Loop Moves
                for move_next in range(-5,6):
                    
                    tic_move = time.perf_counter()
                    simulation_block_next = copy.deepcopy(next_block_copy)
                    simulation_game_state_next = copy.deepcopy(game_state_copy_next)
                    if move_next == 0:
                        #Stay
                        pass
                    elif move_next < 0:
                        for _ in range(move_next,0):
                            if not simulation_block_next.move_left(simulation_game_state_next):
                                break
                    elif move_next > 0:
                        for _ in range(move_next):
                            if not simulation_block_next.move_right(simulation_game_state_next):
                                break

                    # Save positions so we dont calculate them again
                    if simulation_block_next.block_position in positions_next:
                        continue
                    else:
                        positions_next.append(simulation_block.block_position)

                    # Calculate fitness of first and second block
                    simulation_game_state_next = drop_to_end(simulation_game_state_next,simulation_block_next)
                    fitness_next = calculate_fitness(simulation_game_state_next, weights, blocks_used)    
                    final_fitness = fitness + fitness_next


                    if final_fitness > best_fitness:
                        best_fitness = final_fitness
                        best_move = (rotate, move)
                        
            """
            if fitness > best_fitness:
                best_fitness = fitness
                best_move = (rotate, move)
            
    return best_move

def calculate_fitness(game_state, weights, blocks_used):
    
    game_state.check_tetris(0)
    game_state.check_holes()
    game_state.check_height()
    game_state.check_pikes()
    game_state.check_roofs()
    game_state.check_empty_pillars()

    if game_state.check_fail():
        return (weights[0] * game_state.field_used) + (weights[1] * game_state.tetris) + (weights[2] * game_state.holes) + (weights[3] * game_state.difference) + (weights[4] * game_state.roofs) + (weights[5] * game_state.pillars) - 10

    return (weights[0] * game_state.field_used) + (weights[1] * game_state.tetris) + (weights[2] * game_state.holes) + (weights[3] * game_state.difference) + (weights[4] * game_state.roofs) + (weights[5] * game_state.pillars)

def drop_to_end(game_state, current_block):
    current_block.dropped = True
    while current_block.move_down(game_state):
        pass

    game_state.game_state = game_state.set_current_block_to_gamestate(current_block)

    return game_state

if __name__ == "__main__":
    main_loop()