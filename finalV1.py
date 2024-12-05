# speed range: 1.3 - 4 用v8跑的
# 这个版本比较稳定 就是pensonal和公司版本用的同样的代码
import math


class Reward:
    def __init__(self):
        self.first_racingpoint_index = 0

    def reward_function(self, params):

        ################## HELPER FUNCTIONS ###################

        def dist_2_points(x1, x2, y1, y2):
            return abs(abs(x1-x2)**2 + abs(y1-y2)**2)**0.5

        def closest_2_racing_points_index(racing_coords, car_coords):

            # Calculate all distances to racing points
            distances = []
            for i in range(len(racing_coords)):
                distance = dist_2_points(x1=racing_coords[i][0], x2=car_coords[0],
                                         y1=racing_coords[i][1], y2=car_coords[1])
                distances.append(distance)

            # Get index of the closest racing point
            closest_index = distances.index(min(distances))

            # Get index of the second closest racing point
            distances_no_closest = distances.copy()
            distances_no_closest[closest_index] = 999
            second_closest_index = distances_no_closest.index(
                min(distances_no_closest))

            return [closest_index, second_closest_index]

        def dist_to_racing_line(closest_coords, second_closest_coords, car_coords):

            # Calculate the distances between 2 closest racing points
            a = abs(dist_2_points(x1=closest_coords[0],
                                  x2=second_closest_coords[0],
                                  y1=closest_coords[1],
                                  y2=second_closest_coords[1]))

            # Distances between car and closest and second closest racing point
            b = abs(dist_2_points(x1=car_coords[0],
                                  x2=closest_coords[0],
                                  y1=car_coords[1],
                                  y2=closest_coords[1]))
            c = abs(dist_2_points(x1=car_coords[0],
                                  x2=second_closest_coords[0],
                                  y1=car_coords[1],
                                  y2=second_closest_coords[1]))

            # Calculate distance between car and racing line (goes through 2 closest racing points)
            # try-except in case a=0 (rare bug in DeepRacer)
            try:
                distance = abs(-(a**4) + 2*(a**2)*(b**2) + 2*(a**2)*(c**2) -
                               (b**4) + 2*(b**2)*(c**2) - (c**4))**0.5 / (2*a)
            except:
                distance = b

            return distance

        # Calculate which one of the closest racing points is the next one and which one the previous one
        def next_prev_racing_point(closest_coords, second_closest_coords, car_coords, heading):

            # Virtually set the car more into the heading direction
            heading_vector = [math.cos(math.radians(
                heading)), math.sin(math.radians(heading))]
            new_car_coords = [car_coords[0]+heading_vector[0],
                              car_coords[1]+heading_vector[1]]

            # Calculate distance from new car coords to 2 closest racing points
            distance_closest_coords_new = dist_2_points(x1=new_car_coords[0],
                                                        x2=closest_coords[0],
                                                        y1=new_car_coords[1],
                                                        y2=closest_coords[1])
            distance_second_closest_coords_new = dist_2_points(x1=new_car_coords[0],
                                                               x2=second_closest_coords[0],
                                                               y1=new_car_coords[1],
                                                               y2=second_closest_coords[1])

            if distance_closest_coords_new <= distance_second_closest_coords_new:
                next_point_coords = closest_coords
                prev_point_coords = second_closest_coords
            else:
                next_point_coords = second_closest_coords
                prev_point_coords = closest_coords

            return [next_point_coords, prev_point_coords]

        def racing_direction_diff(closest_coords, second_closest_coords, car_coords, heading):

            # Calculate the direction of the center line based on the closest waypoints
            next_point, prev_point = next_prev_racing_point(closest_coords,
                                                            second_closest_coords,
                                                            car_coords,
                                                            heading)

            # Calculate the direction in radius, arctan2(dy, dx), the result is (-pi, pi) in radians
            track_direction = math.atan2(
                next_point[1] - prev_point[1], next_point[0] - prev_point[0])

            # Convert to degree
            track_direction = math.degrees(track_direction)

            # Calculate the difference between the track direction and the heading direction of the car
            direction_diff = abs(track_direction - heading)
            if direction_diff > 180:
                direction_diff = 360 - direction_diff

            return direction_diff
         
        # v6 add function         
        def is_turning(waypoints, closest_waypoints, heading_threshold=15):
            # 获取最近的两个 waypoints 的坐标
            wp1 = waypoints[closest_waypoints[0]]  # 最近的 waypoint
            wp2 = waypoints[closest_waypoints[1]]  # 次最近的 waypoint

            # 计算当前赛道方向（两个 waypoints 的方向）
            track_direction = math.atan2(wp2[1] - wp1[1], wp2[0] - wp1[0])  # 结果为弧度
            track_direction = math.degrees(track_direction)  # 转换为角度

            # 获取下一个赛段的方向变化（与后续 waypoints 比较）
            next_index = (closest_waypoints[1] + 1) % len(waypoints)  # 防止索引越界
            wp3 = waypoints[next_index]  # 下一个 waypoint

            # 计算后续方向
            next_direction = math.atan2(wp3[1] - wp2[1], wp3[0] - wp2[0])  # 弧度
            next_direction = math.degrees(next_direction)  # 转换为角度

            # 计算方向变化
            delta_heading = abs(next_direction - track_direction)
            if delta_heading > 180:
                delta_heading = 360 - delta_heading

            # 判断是否需要拐弯
            is_turn = delta_heading > heading_threshold

            return is_turn, delta_heading

        #################### RACING LINE ######################

        # Optimal racing line for the Spain track
        # Each row: [x,y,speed,timeFromPreviousPoint]
        racing_track = [[3.07915, 0.72447, 4.0, 0.03586],
                        [3.22356, 0.71365, 4.0, 0.03621],
                        [3.36931, 0.70544, 4.0, 0.0365],
                        [3.51609, 0.69955, 4.0, 0.03672],
                        [3.66352, 0.69578, 4.0, 0.03687],
                        [3.81117, 0.69397, 4.0, 0.03692],
                        [3.9587, 0.69401, 4.0, 0.03688],
                        [4.10583, 0.69585, 4.0, 0.03678],
                        [4.25235, 0.69943, 4.0, 0.03664],
                        [4.39814, 0.70477, 4.0, 0.03647],
                        [4.54304, 0.7119, 4.0, 0.03627],
                        [4.68696, 0.72087, 4.0, 0.03605],
                        [4.82981, 0.73171, 4.0, 0.03582],
                        [4.9715, 0.74448, 4.0, 0.03556],
                        [5.11194, 0.75923, 3.91332, 0.03609],
                        [5.25109, 0.77597, 3.56108, 0.03936],
                        [5.38882, 0.79482, 3.21238, 0.04328],
                        [5.52498, 0.81594, 2.87157, 0.04798],
                        [5.65933, 0.8396, 2.54408, 0.05362],
                        [5.865648, 0.830520, 2.25195, 0.05991],
                        [6.083843, 0.867121, 1.98528, 0.06707],
                        [6.200247, 0.898081, 1.75838, 0.07459],
                        [6.391656, 0.976372, 1.5386, 0.08377],
                        [6.469977, 1.018372, 1.42562, 0.08859],
                        [6.547321, 1.066323, 1.42562, 0.08652],
                        [6.624036, 1.121482, 1.42562, 0.08424],
                        [6.689260, 1.179187, 1.3, 0.0897],
                        [6.745975, 1.237716, 1.3, 0.08695],
                        [6.809157, 1.311327, 1.3, 0.08419],
                        [6.852964, 1.376645, 1.3, 0.08173],
                        [6.922941, 1.549017, 1.3, 0.08029],
                        [6.940736, 1.638271, 1.3, 0.07922],
                        [6.949726, 1.721435, 1.3, 0.07503],
                        [6.948867, 1.814583, 1.3, 0.07169],
                        [6.937972, 1.894424, 1.3, 0.07201],
                        [6.889821, 2.047773, 1.3, 0.07278],
                        [6.844840, 2.130820, 1.3, 0.0681],
                        [6.801994, 2.192482, 1.72047, 0.06293],
                        [6.687400, 2.302608, 1.91428, 0.05816],
                        [6.613456, 2.351955, 2.13807, 0.05359],
                        [6.546127, 2.383977, 2.46225, 0.04785],
                        [6.468382, 2.412076, 2.78034, 0.04342],
                        [6.384082, 2.432213, 3.12844, 0.03943],
                        [6.298106, 2.454313, 3.63726, 0.03456],
                        [6.209264, 2.482262, 4.0, 0.03189],
                        [6.119637, 2.498427, 4.0, 0.03224],
                        [6.004240, 2.518878, 4.0, 0.03269],
                        [5.805380, 2.558177, 4.0, 0.03435],
                        [5.586167, 2.602372, 4.0, 0.03453],
                        [5.465429, 2.643546, 4.0, 0.03461],
                        [5.329964, 2.694315, 4.0, 0.03466],
                        [5.181437, 2.759402, 4.0, 0.0347],
                        [5.058739, 2.824707, 4.0, 0.03473],
                        [4.918065, 2.910893, 4.0, 0.03476],
                        [4.792581, 3.005219, 4.0, 0.03479],
                        [4.659780, 3.105202, 4.0, 0.0348],
                        [4.539641, 3.196266, 4.0, 0.03482],
                        [4.417607, 3.280962, 4.0, 0.03483],
                        [4.291364, 3.364265, 4.0, 0.03483],
                        [4.172405, 3.460372, 4.0, 0.03483],
                        [4.067774, 3.551551, 4.0, 0.03483],
                        [3.968615, 3.647253, 1.4, 0.03647],
                        [3.878423, 3.745178, 3.34197, 0.04063],
                        [3.64099, 3.76269, 2.9146, 0.0465],
                        [3.52211, 3.82674, 2.54365, 0.05309],
                        [3.40292, 3.88871, 2.54365, 0.05281],
                        [3.28324, 3.94775, 2.54365, 0.05246],
                        [3.16285, 4.00286, 2.54365, 0.05205],
                        [3.04161, 4.05296, 2.54365, 0.05157],
                        [2.91943, 4.09662, 2.54365, 0.05101],
                        [2.79639, 4.13198, 2.82779, 0.04527],
                        [2.67297, 4.16092, 2.71695, 0.04666],
                        [2.54937, 4.18381, 2.61433, 0.04808],
                        [2.42576, 4.20092, 2.40642, 0.05186],
                        [2.3023, 4.21238, 2.21729, 0.05592],
                        [2.17918, 4.21817, 1.9786, 0.0623],
                        [2.05663, 4.21796, 1.75633, 0.06978],
                        [1.93497, 4.21134, 1.54523, 0.07885],
                        [1.81456, 4.19795, 1.40651, 0.08613],
                        [1.69604, 4.17676, 1.40651, 0.0856],
                        [1.58028, 4.14665, 1.40651, 0.08504],
                        [1.46878, 4.1058, 1.40651, 0.08443],
                        [1.36389, 4.05213, 1.40651, 0.08377],
                        [1.26935, 3.98333, 1.40651, 0.08313],
                        [1.18961, 3.89844, 1.54329, 0.07547],
                        [1.12366, 3.8017, 1.72915, 0.06771],
                        [1.06963, 3.69616, 1.88962, 0.06275],
                        [1.02636, 3.58353, 2.04732, 0.05894],
                        [0.99299, 3.46502, 2.20363, 0.05587],
                        [0.96886, 3.3416, 2.36054, 0.05327],
                        [0.95341, 3.21418, 2.51715, 0.05099],
                        [0.94612, 3.08358, 2.66818, 0.04902],
                        [0.94652, 2.95069, 2.80394, 0.0474],
                        [0.95419, 2.81634, 2.93246, 0.04589],
                        [0.96868, 2.68141, 3.01121, 0.04507],
                        [0.98967, 2.5467, 3.06276, 0.04452],
                        [1.01688, 2.41293, 3.05594, 0.04467],
                        [1.05003, 2.28075, 2.87043, 0.04747],
                        [1.0888, 2.15069, 2.68409, 0.05056],
                        [1.13289, 2.02315, 2.44377, 0.05522],
                        [1.18207, 1.89846, 2.22144, 0.06034],
                        [1.23616, 1.77692, 2.03357, 0.06542],
                        [1.29518, 1.65891, 1.756, 0.07514],
                        [1.35951, 1.54509, 1.756, 0.07446],
                        [1.42956, 1.4362, 1.756, 0.07373],
                        [1.50611, 1.33343, 1.756, 0.07298],
                        [1.59004, 1.23816, 1.756, 0.0723],
                        [1.68227, 1.15201, 1.756, 0.07187],
                        [1.785, 1.07848, 2.05431, 0.0615],
                        [1.89513, 1.01457, 2.14221, 0.05679],
                        [2.01143, 0.95911, 2.49238, 0.0517],
                        [2.13277, 0.91084, 2.68826, 0.04858],
                        [2.2585, 0.86906, 2.91132, 0.04551],
                        [2.38802, 0.83309, 3.10845, 0.04325],
                        [2.52094, 0.80248, 3.32417, 0.04103],
                        [2.65687, 0.77677, 3.52591, 0.03923],
                        [2.79551, 0.75563, 3.89094, 0.03604],
                        [2.9364, 0.73839, 4.0, 0.03549]]

        # planned speed based on waypoints
        # manually adjust the list for better performance, e.g. lower the speed before turning
        above_three_five = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 115, 116, 117]
        above_three = [16, 62, 94, 95, 96, 113, 114]
        above_two_five = [17, 18, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 90, 91, 92, 93, 97, 98, 111, 112]
        above_two = [19, 39, 73, 74, 87, 88, 89, 99, 100, 101, 108, 109, 110]
        above_one_five = [75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 102, 103, 104, 105, 106, 107]
        below_one_five = [20, 21, 22, 23, 24, 25]
        strong_below_one_five = [26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42] # need < 1.3
        # planned speed based on waypoints
        # observe which side the car is expected to run at
        right_track = [52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62]
        center_track = [118, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 62, 96, 97]
        left_track = [i for i in range(0, 119) if i not in right_track + center_track]

        # obvious sides
        strong_center = [0, 1, 2, 3, 4, 5, 6, 7]
        strong_left = [14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 50, 79, 80, 81, 82, 83, 84, 85, 86, 87]
        strong_right = [51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62]
        strong_strong_left = [26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 102, 103, 104, 105, 106, 107, 108, 109]
        hard_strong_strong_left = [26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39]
        ################## INPUT PARAMETERS ###################

        # Read all input parameters
        x = params['x']
        y = params['y']
        xx = round(params['x'], 2)
        yy = round(params['y'], 2)
        distance_from_center = params['distance_from_center']
        is_left_of_center = params['is_left_of_center']
        heading = params['heading']
        progress = params['progress']
        steps = params['steps']
        speed = params['speed']
        steering_angle = abs(params['steering_angle'])
        steering_angle_other = params['steering_angle']
        track_width = params['track_width']
        is_offtrack = params['is_offtrack']
        is_reversed = params['is_reversed']
        waypoints = params["waypoints"]
        closest_waypoints = params["closest_waypoints"]

        ############### OPTIMAL X,Y,SPEED,TIME ################

        # Get closest indexes for racing line (and distances to all points on racing line)
        closest_index, second_closest_index = closest_2_racing_points_index(
            racing_track, [x, y])

        # Get optimal [x, y, speed, time] for closest and second closest index
        optimals = racing_track[closest_index]
        optimals_second = racing_track[second_closest_index]

        if steps == 1:
            self.first_racingpoint_index = closest_index

        ################ REWARD AND PUNISHMENT ################
        reward = 1e-3

        # Zero reward if off track ##
        if is_offtrack or is_reversed:
            return reward

        # Zero reward if obviously wrong direction (e.g. spin)
        direction_diff = racing_direction_diff(
            optimals[0:2], optimals_second[0:2], [x, y], heading)
        if direction_diff > 30:
            return reward

        # Reward if car goes close to optimal racing line
        def get_distance_reward(threshold, distance, multiplier):
            distance_reward = max(0, 1 - (distance / threshold))

            return distance_reward * multiplier

        DIST_THRESH = track_width * 0.5
        dist = dist_to_racing_line(optimals[0:2], optimals_second[0:2], [x, y])
        
        ideal_heading = 0
        if (distance_from_center < 0.01 * track_width):
            if closest_index in center_track:
                reward += get_distance_reward(DIST_THRESH, dist, 1)
            if closest_index in strong_center:
                # Check if heading is close to the ideal heading (straight line)
                heading_deviation = abs(heading - ideal_heading)  # Deviation from ideal heading       
                if heading_deviation < 2:
                    reward += get_distance_reward(DIST_THRESH, dist, 5)
                elif heading_deviation >= 2 and heading_deviation < 5:
                    reward *=0.5
                elif heading_deviation > 5:
                    reward = 1e-3

                if speed < 3:
                    reward = 1e-3
        elif is_left_of_center:
            if closest_index in left_track:
                reward += get_distance_reward(DIST_THRESH, dist, 1)
            if closest_index in strong_left:
                reward += get_distance_reward(DIST_THRESH, dist, 3)
            if closest_index in strong_strong_left:
                if 0.3 * track_width < distance_from_center < 0.4 * track_width and speed < 1.5:
                    reward += get_distance_reward(DIST_THRESH, dist, 5)
                else:
                    if speed <= 1.4:
                        reward += get_distance_reward(DIST_THRESH, dist, 3)
                    else:
                        reward = 1e-3
                if closest_index in hard_strong_strong_left:
                    if steering_angle_other < 0 and steering_angle > 5: # can't turn right
                        reward = 1e-3
                    
                    
                    
            if closest_index in strong_right:
                reward *=0.5
            is_turn, delta_heading = is_turning(waypoints, closest_waypoints)
            if is_turn and speed > 1.5:
                reward *=0.1                    
        else:
            if closest_index in right_track:
                reward += get_distance_reward(DIST_THRESH, dist, 1)
            if closest_index in strong_right:
                reward += get_distance_reward(DIST_THRESH, dist, 5)
            if closest_index in strong_left:
                reward *=0.5
            if closest_index in strong_strong_left:
                reward = 1e-3

        def get_speed_reward(ceiling, threshold, diff):
            return ceiling - diff/threshold

        # Reward if speed falls within optimal range
        PENALTY_RATIO = 0.9
        SPEED_DIFF_NO_REWARD = 1
        speed_diff = abs(optimals[2]-speed)
        if speed_diff > SPEED_DIFF_NO_REWARD:
            return 1e-3

        if closest_index in above_three_five:
            if speed >= 3.5:
                reward += get_speed_reward(0.5, SPEED_DIFF_NO_REWARD, speed_diff)
            if steering_angle > 3:
                reward *= PENALTY_RATIO
            if speed <= 1.4:
                reward *= 0.1
        elif closest_index in above_three:
            if speed >= 3:
                reward += get_speed_reward(0.5, SPEED_DIFF_NO_REWARD, speed_diff)
            if steering_angle > 8:
                reward *= PENALTY_RATIO
            if speed <= 1.4:
                reward *= 0.1
        elif closest_index in above_two_five:
            if speed >= 2.5:
                reward += get_speed_reward(0.8, SPEED_DIFF_NO_REWARD, speed_diff)
            if steering_angle > 15:
                reward *= PENALTY_RATIO
            if speed <= 1.4:
                reward *= 0.1
        elif closest_index in above_two:
            if speed >= 2:
                reward += get_speed_reward(1, SPEED_DIFF_NO_REWARD, speed_diff)
            if speed <= 1.4:
                reward *= 0.1
        elif closest_index in above_one_five:
            if speed >= 1.5:
                reward += get_speed_reward(3, SPEED_DIFF_NO_REWARD, speed_diff)
        elif closest_index in below_one_five:
            if 1.3 < speed < 1.5:
                reward += get_speed_reward(4, SPEED_DIFF_NO_REWARD, speed_diff)
            if speed >= 1.6:
                reward *= PENALTY_RATIO
        else: 
            if 1.1 < speed < 1.3:
                reward += get_speed_reward(5, SPEED_DIFF_NO_REWARD, speed_diff)
            if speed >= 1.4:
                reward *= 0.5

        # Incentive for finishing the lap in less steps ##
        REWARD_FOR_FASTEST_TIME = 2000 # should be adapted to track length and other rewards
        TARGET_STEPS = 110
        if progress == 100:
            reward += REWARD_FOR_FASTEST_TIME / (steps - TARGET_STEPS)

        #################### RETURN REWARD ####################

        # Always return a float value
        return float(reward)


reward_object = Reward()


def reward_function(params):
    return reward_object.reward_function(params)
