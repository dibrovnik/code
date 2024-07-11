import numpy as np
import matplotlib.pyplot as plt
num_experiments = 6000
import time

# Параметры симуляции
area_size = 50  # квадратные километры
num_uavs = 10  # количество базовых станций UAV
flight_height_min = 50  # метры
flight_height_max = 100  # метры
time_slot_duration = 30  # секунды
total_time_slots = 100
alpha = 9.6117
beta = 0.1581
noise_power = 1e-15  # Вт
SINR_threshold = 0  # дБ
horizontal_speed = 10  # м/с
vertical_speed = 5  # м/с
transmit_power = 0.5  # Вт
bandwidth = 1e6  # 1 МГц
data_rate_requirement = [0.1, 1]  # Мбит/с

# Функции для инициализации и обновления пользователей
def initialize_users(area_size, total_time_slots):
    return np.random.rand(total_time_slots, area_size, area_size)

def update_user_distribution(users, t, area_size):
    users[t, :, :] = np.random.rand(area_size, area_size)

# Функция для разделения области на подблоки
def partition_area(area_size, num_partitions):
    partition_size = area_size // np.sqrt(num_partitions)
    return int(partition_size)

# Функция для назначения базовых станций UAV подблокам
def assign_uavs_to_partitions(partition_size, num_uavs, area_size):
    uav_positions = []
    for _ in range(num_uavs):
        x_partition = np.random.randint(0, area_size, partition_size)
        y_partition = np.random.randint(0, area_size, partition_size)
        height = np.random.uniform(flight_height_min, flight_height_max)
        uav_positions.append([x_partition.mean(), y_partition.mean(), height])
    return np.array(uav_positions)

# Функция для перераспределения базовых станций UAV
def redeploy_uavs(uav_positions, users, area_size, t, flight_height_min, flight_height_max, horizontal_speed, vertical_speed, transmit_power, bandwidth, SINR_threshold, noise_power, alpha, beta):
    for i in range(uav_positions.shape[0]):
        user_demand = users[t, int(uav_positions[i, 0]), int(uav_positions[i, 1])]
        if user_demand < 0.5:  # пример логики перераспределения
            uav_positions[i, 0] = (uav_positions[i, 0] + horizontal_speed * np.random.choice([-1, 1])) % area_size
            uav_positions[i, 1] = (uav_positions[i, 1] + horizontal_speed * np.random.choice([-1, 1])) % area_size
            uav_positions[i, 2] = np.clip(uav_positions[i, 2] + vertical_speed * np.random.choice([-1, 1]), flight_height_min, flight_height_max)
    return uav_positions

# Адаптивный метод распределения UAV BSs
def adaptive_redeploy_uavs(uav_positions, users, area_size, t, flight_height_min, flight_height_max, horizontal_speed, vertical_speed, transmit_power, bandwidth, SINR_threshold, noise_power, alpha, beta):
    for i in range(uav_positions.shape[0]):
        x, y, height = uav_positions[i]
        user_demand = users[t, int(x), int(y)]
        
        if user_demand < 0.5:  # условие для перераспределения
            # Применение алгоритма оптимизации или адаптивного метода для изменения позиций
            # Пример: ройный алгоритм для оптимизации позиций
            new_x = x + horizontal_speed * np.random.uniform(-1, 1)
            new_y = y + horizontal_speed * np.random.uniform(-1, 1)
            new_height = np.clip(height + vertical_speed * np.random.uniform(-1, 1), flight_height_min, flight_height_max)
            
            # Проверка границ области
            new_x = new_x % area_size
            new_y = new_y % area_size
            
            uav_positions[i] = [new_x, new_y, new_height]
    
    return uav_positions

# Функция для оценки качества обслуживания (QoS)
def evaluate_qos(uav_positions, users, bandwidth, SINR_threshold, noise_power):
    QoS = np.random.rand()  # пример оценки качества
    return QoS

# Функция для сглаживания данных
def smooth_data(data, window_size=5):
    return np.convolve(data, np.ones(window_size)/window_size, mode='valid')

# Проведение 50 экспериментов

improvement_ratios_padr = []
improvement_ratios_adaptive = []
start_time = time.time()

for exp in range(num_experiments):
    # Основной цикл симуляции для базового подхода
    users = initialize_users(area_size, total_time_slots)
    results_basic = np.zeros(total_time_slots)

    for t in range(total_time_slots):
        update_user_distribution(users, t, area_size)
        uav_positions = redeploy_uavs(np.random.rand(num_uavs, 3) * area_size, users, area_size, t, flight_height_min, flight_height_max, horizontal_speed, vertical_speed, transmit_power, bandwidth, SINR_threshold, noise_power, alpha, beta)
        QoS = evaluate_qos(uav_positions, users, bandwidth, SINR_threshold, noise_power)
        results_basic[t] = QoS

    # Основной цикл симуляции для подхода PADR
    users = initialize_users(area_size, total_time_slots)
    partition_size = partition_area(area_size, num_uavs)
    uav_positions = assign_uavs_to_partitions(partition_size, num_uavs, area_size)
    results_padr = np.zeros(total_time_slots)

    for t in range(total_time_slots):
        update_user_distribution(users, t, area_size)
        uav_positions = redeploy_uavs(uav_positions, users, area_size, t, flight_height_min, flight_height_max, horizontal_speed, vertical_speed, transmit_power, bandwidth, SINR_threshold, noise_power, alpha, beta)
        QoS = evaluate_qos(uav_positions, users, bandwidth, SINR_threshold, noise_power)
        results_padr[t] = QoS

    # Основной цикл симуляции для адаптивного подхода
    users = initialize_users(area_size, total_time_slots)
    uav_positions = assign_uavs_to_partitions(partition_size, num_uavs, area_size)  # начальное размещение для адаптивного подхода
    results_adaptive = np.zeros(total_time_slots)

    for t in range(total_time_slots):
        update_user_distribution(users, t, area_size)
        uav_positions = adaptive_redeploy_uavs(uav_positions, users, area_size, t, flight_height_min, flight_height_max, horizontal_speed, vertical_speed, transmit_power, bandwidth, SINR_threshold, noise_power, alpha, beta)
        QoS = evaluate_qos(uav_positions, users, bandwidth, SINR_threshold, noise_power)
        results_adaptive[t] = QoS

    # Вычисление средних значений QoS
    average_basic = np.mean(results_basic)
    average_padr = np.mean(results_padr)
    average_adaptive = np.mean(results_adaptive)

    # Вычисление коэффициентов прироста
    improvement_ratio_padr = (average_padr - average_basic) / average_basic * 100
    improvement_ratio_adaptive = (average_adaptive - average_basic) / average_basic * 100

    # Добавление коэффициентов прироста в списки
    improvement_ratios_padr.append(improvement_ratio_padr)
    improvement_ratios_adaptive.append(improvement_ratio_adaptive)

# Вывод средних значений коэффициентов прироста
mean_improvement_ratio_padr = np.mean(improvement_ratios_padr)
mean_improvement_ratio_adaptive = np.mean(improvement_ratios_adaptive)

end_time = time.time()
execution_time = end_time - start_time
print(f'Nums of experiments: {num_experiments}')
print(f'Average Improvement Ratio (PADR vs Basic): {mean_improvement_ratio_padr:.2f}%')
print(f'Average Improvement Ratio (Adaptive vs Basic): {mean_improvement_ratio_adaptive:.2f}%')
print(f'Total execution time: {execution_time:.2f} seconds')
