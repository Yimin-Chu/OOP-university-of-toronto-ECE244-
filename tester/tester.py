"""
pip install pexpect
"""
import pexpect49 as pexpect # the pexpect 4.9 version directly downloaded as a folder, so 
import time
import shutil
import os
import subprocess
from dataclasses import dataclass
from typing import List, Tuple
from itertools import permutations
import json, csv

DEBUG_MODE = 0
COMPILE = False
INCREASE_FPS = False
FPS = 60
SAVE_REFERENCE_SOLUTION = True
MAKE_VIDEO = False
TEST_CASES = [
    # (20,"aim_at_nearest_ball"),
    (1,"quit2"),
    (1,"quit10"),
    (1,"quit40"),
    (0,"nothing"),
    (1,"aim_away_from_nearest_ball"),
    (2,"aim_at_nearest_ball"),
    (5,"aim_at_nearest_ball"),
    # (11,"aim_at_nearest_ball"),
]
tester_errors = []
# change the io.cpp file to stop code from clearing the console, we this script can capture the outputs. After generating executable, change it back
def modify_cpp(file_path, replacements):
    backup_path = file_path + '.bak'
    shutil.copy(file_path, backup_path)
    with open(file_path, 'r') as file:
        content = file.read()
        for keyword, replacement in replacements:
            content = content.replace(keyword,replacement)
    with open(file_path, 'w') as file:
        file.write(content)
def undo_modify_cpp(file_path):
    backup_path = file_path + '.bak'
    if backup_path and os.path.exists(backup_path):
        shutil.copy(backup_path, file_path)
        os.remove(backup_path)
    else:
        print("No backup found or backup path is invalid.")


#Find all instances of some char on game board. Return the list of coordinates
def find_coordinates(board, char):
    coordinates = []
    lines = board.strip().split('\n')
    for y, line in enumerate(lines):
        for x, ch in enumerate(line):
            if ch == char:
                coordinates.append((x, y))
    return coordinates

# Function to decide the input based on game output, by tracking the ball. 
def decide_control_signal(frame, ith_frame, policy="aim_at_nearest_ball"):
    
    # Find the row index of the first/last row that contains the char. This helps with finding the player's position
    def find_min_row_with_char(grid, char):
        rows = grid.strip().split('\n')
        for index, row in enumerate(rows):
            if char in row:
                return index
        return None
    def find_max_row_with_char(grid, char):
        rows = grid.strip().split('\n')
        for index, row in reversed(list(enumerate(rows))):
            if char in row:
                return index
        return None
    frame=frame.replace("Your score is:","") # get ride of the score

    ball_coords = find_coordinates(frame,"o") # there can be lots of balls
    player_height_min = find_min_row_with_char(frame,"#")
    player_height_max = find_max_row_with_char(frame,"#")
    
    if player_height_min == None or player_height_max ==None:
        return None,"Error: no player paddle found, meaning your game does not have any [#] character on the board"
    if len(ball_coords)==0:
        return None,"Error: no ball found, meaning your game does not have any [o] character on the board"

    player_height_midpoint = (player_height_min+player_height_max)/2
    # sort by how close the ball is to player
    ball_coords.sort(key=lambda coord: (coord[0], coord[1])) 
    closest_ball_height = ball_coords[0][1] # aim at the nearest ball. 
    if policy.startswith("quit") and int(policy.replace("quit",""))==ith_frame:
        return 'q', None #nothing
    if policy=="aim_at_nearest_ball":
        if player_height_midpoint<closest_ball_height:
            return "B",None # up
        elif player_height_midpoint>closest_ball_height:
            return 'A',None
    elif policy=="aim_away_from_nearest_ball":
        if player_height_midpoint<closest_ball_height:
            return 'A',None
        elif player_height_midpoint>closest_ball_height:
            return 'B',None
    return 'C',None # nothing.

PASS = "PASS"

@dataclass
class FrameData:
    game_ended: bool
    width: int # not tested?
    height: int # not tested?
    frame_num: int
    score: int
    ball_coordinates: List[Tuple[int, int]]
    paddle_height: int
    paddle_top_coordinate: Tuple[int, int] = None
    error_messages: List[str] = None
    received_input: str = ""
    fps: float = 0

    @classmethod
    def from_frame(cls, frame: str): #-> error_message, FrameData:
        error_messages = []
        # sanity checks
        if frame.count("This is frame") != 1: 
            return "More than one occurance of [This is frame] in game frame.", None
        if frame.count("Your score is:") != 1:
            return "More than one occurance of [Your score is:] in game frame.", None

        # whether game has ended
        keywords = ['Game Over.','Game over.', 'game over.', 'gameover.']
        game_ended = any(keyword in frame for keyword in keywords)
        for keyword in keywords + ["A",'B','C','q']: #control characters 
            frame = frame.replace(keyword, '')
        
        # frame_num and score
        rest_of_frame, received_input = frame.split("Received input:", 1)
        rest_of_frame, frame_num = rest_of_frame.split("This is frame", 1)
        rest_of_frame, score = rest_of_frame.split("Your score is:", 1)
        received_input = received_input.lstrip("[").rstrip("]").strip()
        
        frame_num = int(frame_num.strip())
        score = int(score.strip())

        # frame dimensions
        board = rest_of_frame.strip() 
        board_lines = [line.rstrip() for line in board.splitlines()]
        height = len(board_lines) - 2
        width = (max(len(line) for line in board_lines) - 2) if height > 0 else 0
        if any(len(line) != width+2 for line in board_lines):
            
            return f"Frame is not a rectangle:~~~\n{frame}\n~~~", None

        # Check if the frame is surrounded by walls of '|' and '-'
        if not (board_lines[0].strip() == '-' * (width + 2) and board_lines[-1].strip() == '-' * (width + 2)):
            return "Frame is not surrounded by - on top and bottom", None
        for line in board_lines[1:-1]:
            if not (line[0] == '|' and line[-1] == '|'):
                return "Frame is not surrounded by | on sides", None
        if game_ended==True:
            paddle_height = PASS
            paddle_top_coordinate = PASS
            ball_coordinates = PASS
            return None, cls(game_ended,width, height, frame_num, score, ball_coordinates, paddle_height, paddle_top_coordinate, error_messages, received_input, 0) 

        # ball and paddle pixel coordinates
        ball_coordinates = find_coordinates(board,"o")
        paddle_pixel_coordinates = find_coordinates(board,"#")
        paddle_height = len(paddle_pixel_coordinates)

        # Check if the paddle is in a straight vertical line and continuous
        if paddle_height == 0:
            return "No paddle found in game. This means your game does not have any [#] character on the board", None
        if any(pos[0] != paddle_pixel_coordinates[0][0] for pos in paddle_pixel_coordinates):
            error_messages.append("Paddle is not in a straight vertical line. This means not all [#] characters are in the same column")
        if paddle_height > 1:
            paddle_pixel_coordinates_sorted = sorted(paddle_pixel_coordinates, key=lambda pos: pos[1])
            if any(paddle_pixel_coordinates_sorted[i][1] + 1 != paddle_pixel_coordinates_sorted[i+1][1] for i in range(paddle_height - 1)):
                error_messages.append("Paddle is not a continuous vertical line, this means there is a gap between some [#] characters")
        
        paddle_top_coordinate = paddle_pixel_coordinates_sorted[0]

        return None, cls(game_ended,width, height, frame_num, score, ball_coordinates, paddle_height, paddle_top_coordinate, error_messages, received_input, 0) 


def find_minimum_mapping(points1, points2):
    def euclidean_distance(p1, p2):
        return ((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2) ** 0.5
    
    def min_cost_bipartite_matching(cost_matrix):
        n = len(cost_matrix)
        min_cost = float('inf')
        best_perm = None
        for perm in permutations(range(n)):
            cost = sum(cost_matrix[i][perm[i]] for i in range(n))
            if cost < min_cost:
                min_cost = cost
                best_perm = perm
        return min_cost, best_perm

    n = len(points1)
    if n != len(points2):
        raise ValueError("Both lists must have the same number of points")

    # Create the cost matrix
    cost_matrix = [[euclidean_distance(p1, p2) for p2 in points2] for p1 in points1]

    # Find the minimum cost and best permutation
    min_cost, best_perm = min_cost_bipartite_matching(cost_matrix)

    # Return the minimum cost and the permutation
    return min_cost



def save_to_json(frame_data_list, filename):
    # Convert the FrameData objects to dictionaries
    data_to_save = [
        {
            'game_ended': frame.game_ended,
            'height': frame.height,
            'width': frame.width,
            'frame_num': frame.frame_num,
            'score': frame.score,
            'ball_coordinates': frame.ball_coordinates,
            'paddle_height': frame.paddle_height,
            'paddle_top_coordinate': frame.paddle_top_coordinate
        }
        for frame in frame_data_list
    ]
    with open(filename, 'w') as file:
        json.dump(data_to_save, file, indent=4)
def save_to_csv(frame_data_list, filename):
    fieldnames = ['game_ended', 'height', 'width', 'frame_num', 'score', 'num_balls', 'ball_coordinates', 'paddle_height', 'paddle_top_coordinate']
    with open(filename, 'w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for frame_data in frame_data_list:
            writer.writerow({
                'game_ended': frame_data.game_ended,
                'height': frame_data.height,
                'width': frame_data.width,
                'frame_num': frame_data.frame_num,
                'score': frame_data.score,
                'num_balls': len(frame_data.ball_coordinates),
                'ball_coordinates': frame_data.ball_coordinates,
                'paddle_height': frame_data.paddle_height,
                'paddle_top_coordinate': frame_data.paddle_top_coordinate
            })
def read_from_json(filename):
    # print(os.path.abspath(__file__),os.listdir('reference_solution_outputs'))
    with open(filename, 'r') as file:
        data_loaded = json.load(file)
    frame_data_list = [
        FrameData(
            game_ended=data['game_ended'],
            height=data['height'],
            width=data['width'],
            frame_num=data['frame_num'],
            score=data['score'],
            ball_coordinates=[tuple(coord) for coord in data['ball_coordinates']],
            paddle_height=data['paddle_height'],
            paddle_top_coordinate=tuple(data['paddle_top_coordinate'])
        )
        for data in data_loaded
    ]
    return frame_data_list


def run_game(TARGET_SCORE=0, policy="aim_at_nearest_ball",max_frames=10000, verbose=False, record_frames = False):
    # Start the game
    game = pexpect.spawn('./game')
    game.delaybeforesend = 0 # don't delay before sending keys. Hopefully this wont causes issues
    
    error_message = None
    frame_data_list = []
    if record_frames: frame_recordings = []
    prev_time = time.time()
    control_signal = ""
    try:
        for i in range(max_frames):
            game.expect_exact('!')
            frame = game.before.decode().strip()
            
            error_message, frame_data = FrameData.from_frame(frame)
            if frame_data is None:
                error_message = f"Game stopped on frame {i} because of error: {error_message}"
                break
            if frame_data.frame_num != i:
                error_message = f"Game stopped on frame {i} because of error: missing frame. Expecting frame {i}, gotten frame {frame_data.frame_num}. This means your game is skipping frames or having duplicated frames. This may or may not be your fault, please consult the TA by piazza or email."
                break

            if not frame_data.game_ended: # check the control signal 
                if control_signal != "": control_signal = str(ord(control_signal))
                if frame_data.received_input != control_signal:
                    error_message = f"Game stopped on frame {i} because control signal by the tester is not received by the game (this is not your fault, it means the testers is broken and the TA is about to have a bad day); Please send this debug entire debug message to the TA: |{frame_data.received_input}|{control_signal}|"
                    tester_errors.append(error_message)
                    break
            # send keypress to move up or down
            if not frame_data.game_ended and frame_data.score<TARGET_SCORE:
                control_signal, error_message = decide_control_signal(frame, i, policy=policy)
                if error_message is None: 
                    game.send(control_signal)
                else:
                    error_message = f"Game stopped on frame {i} because of error: {error_message}"
                    break
            else:
                control_signal = ""

            cur_time = time.time()
            if verbose:
                recording_frame=frame+"\n"
                recording_frame+=f"> frame {i}, frame len is {len(frame)} chars, fps is  {1/(cur_time-prev_time)}"
                print(recording_frame, frame_data, error_message)
            if record_frames:
                recording_frame=frame+"\n"
                recording_frame+=f"> frame {i}, frame len is {len(frame)} chars, fps is  {1/(cur_time-prev_time)}"
                assert error_message == None
                assert len(tester_errors) == 0
                frame_recordings.append(recording_frame)
            frame_data.fps = 1/(cur_time-prev_time) if (i not in [0,1]) else PASS
            frame_data_list.append(frame_data)
            prev_time = cur_time
    except pexpect.exceptions.EOF:
        if verbose: print("The game has ended.")
    except pexpect.exceptions.TIMEOUT:
        error_message = error_message if error_message else "" + "\nThe game timed out"
        if verbose: print("The game timed out")
    except Exception as e:
        error_message = error_message if error_message else "" +  f"\nAn unknown error occurred. This error message may or may not make sense, please consult the TA by piazza or email: {e}"
        if verbose: print(f"An error occurred: {e}")
    finally:
        game.close()
    if record_frames: return frame_recordings
    return frame_data_list, error_message


def compare_frame_data(ref,student):
    result = {}
    
    #score changes
    result["score"] = ref.score, student.score, 0

    #fps 
    if FPS == 60:
        FPS_tolerance = 5
    elif FPS < 200:
        FPS_tolerance = int(FPS*0.1)
    else: #if FPS > 200, allow any FPS 
        FPS_tolerance = FPS    
    result["fps"] = FPS, student.fps, FPS_tolerance  

    #number of balls
    student_ball_len = PASS if (student.ball_coordinates==PASS) else len(student.ball_coordinates)
    result["ball count"] = len(ref.ball_coordinates), student_ball_len, 0
    if student_ball_len!=len(ref.ball_coordinates): return result
    
    #physics
    average_ball_loc_diff = find_minimum_mapping(ref.ball_coordinates, student.ball_coordinates)/len(ref.ball_coordinates)
    TOLERATED_DIFF = 2
    result["average ball location difference"] = 0, average_ball_loc_diff, TOLERATED_DIFF
    
    #player control
    result["paddle_top_coordinate"] = len(ref.paddle_top_coordinate), len(student.paddle_top_coordinate), 1
    result["paddle_height"] = ref.paddle_height, student.paddle_height, 0

    return result

def check_tolerance(result):
    error_lists = []
    for key, (ref, student, tolerance) in result.items():
        if student == PASS:
            continue
        if abs(ref-student)>tolerance:
            error_lists.append( f"Error: {key} = [{student}], the referenece solution have [{ref}]; the tolerance is +-{tolerance}")
    if error_lists:
        return False, " | ".join(error_lists)
    return True, None

def compare_frame_data_list(ref, student): # missing DTW
    result = {}    
    # get episode length 
    result["Length of the game in number of frames (if this is wrong, it means your game ended too early or late)"] = len(ref), len(student), int(0.1*len(ref)+1)
    if len(student)==0: return result, []

    # get wall size
    result["wall width"] = ref[0].width, student[0].width, 0
    result["wall height"] = ref[0].height, student[0].height, 0
    
    # whether game ended
    result["game has ended"] = ref[-1].game_ended, student[-1].game_ended, 0
    if ref[-1].game_ended != student[-1].game_ended:
        return result, []
    bad_frame_count = 0
    frame_errors = [] 
    for i in range( min(len(student), len(ref))):
        passed, error_message = check_tolerance(compare_frame_data(ref[i], student[i]))
        if not passed:
            bad_frame_count+=1 
            frame_errors.append(f"Frame {i}: {error_message}")
            if len(student[i].error_messages)>0:
                frame_errors.append(f"Frame {i}: {' | '.join(student[i].error_messages)}")
    result["You have too many frames that are wrong: a few wrong frames is ok but you have"] = 0, bad_frame_count, int(0.2*len(ref))+1
    return result, frame_errors

def run_test(TARGET_SCORE, policy, verbose=False,print_output=False, save_output=False):
    true_answer = read_from_json(f'reference_solution_outputs/reference_solution_frame_datas_{TARGET_SCORE}_{policy}.json')
    frame_data_list, game_error_message = run_game(TARGET_SCORE, policy, verbose=verbose)
    result, frame_errors = compare_frame_data_list(true_answer, frame_data_list)
    passed, critical_error_message = check_tolerance(result)
    output = ""
    output += 'PASSED\n' if passed else 'FAILED\n'
    output += "=========================================\n"
    output += f"Game error message: \n{game_error_message}\n\n"
    output += "=========================================\n"
    output += f"Critical error message: \n{critical_error_message}\n\n"
    output += "=========================================\n"
    output += f"Errors in individual frames: {'(which your amount of bad frame is acceptable)' if passed else ''}\n"
    for error in frame_errors:
        output += "\t" + error + "\n"
    if print_output:
        print(output)
    if save_output:
        with open(f"test_results{TARGET_SCORE}.txt", "w") as file:
            file.write(output)    
    return passed

if __name__ == "__main__":
    if COMPILE:
        subprocess.run(['make','clean'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        replacements = [
            ['#define RUNNING_WITH_PYTHON_TESTER 0','#define RUNNING_WITH_PYTHON_TESTER 1'],
        ]
        if INCREASE_FPS:   
            replacements.append(["screen_fps 60",f"screen_fps {FPS}"])
        modify_cpp('Globals.h',replacements)
        subprocess.run(['make','game'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        undo_modify_cpp('Globals.h')

    if MAKE_VIDEO:
        from text_to_mp4 import generate_image
        frames = run_game(20,"aim_at_nearest_ball", record_frames=True)
        print(frames)
        generate_image(frames,prolong_last_frame=300)
        exit()

    if SAVE_REFERENCE_SOLUTION:
        for TARGET_SCORE, policy in TEST_CASES:
            frame_data_list,game_error_message = run_game(TARGET_SCORE,policy, verbose=True)
            assert game_error_message == None, game_error_message
            for frame_data in frame_data_list:
                assert len(frame_data.error_messages)==0, "\n".join(frame_data.error_messages)
            if not os.path.exists('reference_solution_outputs'):
                os.makedirs('reference_solution_outputs')

            save_to_json(frame_data_list, f'reference_solution_outputs/reference_solution_frame_datas_{TARGET_SCORE}_{policy}.json')
            save_to_csv(frame_data_list, f'reference_solution_outputs/reference_solution_frame_datas_{TARGET_SCORE}_{policy}.csv')
            time.sleep(1) # for no reason other than helping me knowing a new game has started 

    if not SAVE_REFERENCE_SOLUTION:
        for TARGET_SCORE,policy in TEST_CASES:
            run_test(TARGET_SCORE,policy)
            assert len(tester_errors)==0, "\n".join(tester_errors)
            
