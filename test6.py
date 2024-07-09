import numpy as np
import matplotlib.pyplot as plt
from joblib import Parallel, delayed
import time

num_experiments = 50

# Параметры симуляции
area_size = 280  # квадратные километры
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

# Функция для перераспределения базовых станций UAV (базовый подход)
def redeploy_uavs(uav_positions, users, area_size, t, flight_height_min, flight_height_max, horizontal_speed, vertical_speed, transmit_power, bandwidth, SINR_threshold, noise_power, alpha, beta):
    for i in range(uav_positions.shape[0]):
        user_demand = users[t, int(uav_positions[i, 0]), int(uav_positions[i, 1])]
        if user_demand < 0.5:  # условие для перераспределения
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

def evaluate_qos(uav_positions, users, bandwidth, SINR_threshold, noise_power):
    total_capacity = 0
    
    for i in range(uav_positions.shape[0]):
        x, y, height = uav_positions[i]
        t = np.random.randint(users.shape[0])  # Choose a random time slot
        user_demand = users[t, int(x), int(y)] if t < users.shape[0] else 0
        
        if user_demand > 0.5:  # условие для обслуживания
            # Оценка SINR
            SINR = transmit_power / (noise_power + interference(uav_positions, i, height, transmit_power))
            
            # Оценка пропускной способности по формуле Шеннона-Хартли
            capacity = bandwidth * np.log2(1 + SINR)
            total_capacity += capacity
    
    # Средняя пропускная способность
    average_capacity = total_capacity / uav_positions.shape[0]
    
    # Возвращаем QoS как среднюю пропускную способность
    return average_capacity


# Функция для оценки межуровневых помех
def interference(uav_positions, index, height, transmit_power):
    total_interference = 0
    
    for j in range(uav_positions.shape[0]):
        if j != index:
            x_j, y_j, height_j = uav_positions[j]
            distance_sq = (x_j - uav_positions[index, 0])**2 + (y_j - uav_positions[index, 1])**2 + (height_j - height)**2
            path_loss = alpha * np.log10(np.sqrt(distance_sq))
            interference_power = transmit_power / path_loss
            total_interference += interference_power
    
    return total_interference + noise_power

# Функция для оценки энергоэффективности
def evaluate_energy_efficiency(uav_positions, transmit_power, bandwidth, area_size):
    total_transmit_power = np.sum(transmit_power for uav_position in uav_positions)
    energy_efficiency = total_transmit_power / area_size
    return energy_efficiency

# Основная функция для запуска эксперимента
def run_experiment(seed):
    np.random.seed(seed)
    
    # Инициализация пользователей и UAV BSs
    users = initialize_users(area_size, total_time_slots)
    uav_positions_basic = np.random.rand(num_uavs, 3) * area_size
    uav_positions_padr = assign_uavs_to_partitions(partition_area(area_size, num_uavs), num_uavs, area_size)
    uav_positions_adaptive = assign_uavs_to_partitions(partition_area(area_size, num_uavs), num_uavs, area_size)
    
    results_basic = np.zeros(total_time_slots)
    results_padr = np.zeros(total_time_slots)
    results_adaptive = np.zeros(total_time_slots)
    
    start_time_experiment = time.time()
    
    for t in range(total_time_slots):
        update_user_distribution(users, t, area_size)
        
        # Базовый подход
        uav_positions_basic = redeploy_uavs(uav_positions_basic, users, area_size, t, flight_height_min, flight_height_max, horizontal_speed, vertical_speed, transmit_power, bandwidth, SINR_threshold, noise_power, alpha, beta)
        QoS_basic = evaluate_qos(uav_positions_basic, users, bandwidth, SINR_threshold, noise_power)
        energy_efficiency_basic = evaluate_energy_efficiency(uav_positions_basic, transmit_power, bandwidth, area_size)
        results_basic[t] = QoS_basic
        
        # PADR
        uav_positions_padr = redeploy_uavs(uav_positions_padr, users, area_size, t, flight_height_min, flight_height_max, horizontal_speed, vertical_speed, transmit_power, bandwidth, SINR_threshold, noise_power, alpha, beta)
        QoS_padr = evaluate_qos(uav_positions_padr, users, bandwidth, SINR_threshold, noise_power)
        energy_efficiency_padr = evaluate_energy_efficiency(uav_positions_padr, transmit_power, bandwidth, area_size)
        results_padr[t] = QoS_padr
        
        # Адаптивный подход
        uav_positions_adaptive = adaptive_redeploy_uavs(uav_positions_adaptive, users, area_size, t, flight_height_min, flight_height_max, horizontal_speed, vertical_speed, transmit_power, bandwidth, SINR_threshold, noise_power, alpha, beta)
        QoS_adaptive = evaluate_qos(uav_positions_adaptive, users, bandwidth, SINR_threshold, noise_power)
        energy_efficiency_adaptive = evaluate_energy_efficiency(uav_positions_adaptive, transmit_power, bandwidth, area_size)
        results_adaptive[t] = QoS_adaptive
    
    end_time_experiment = time.time()
    experiment_duration = end_time_experiment - start_time_experiment
    
    # Вычисление коэффициентов прироста
    average_basic = np.mean(results_basic)
    average_padr = np.mean(results_padr)
    average_adaptive = np.mean(results_adaptive)
    
    improvement_ratio_padr = (average_padr - average_basic) / average_basic * 100
    improvement_ratio_adaptive = (average_adaptive - average_basic) / average_basic * 100
    
    # Оценка энергоэффективности
    average_energy_efficiency_basic = np.mean([evaluate_energy_efficiency(uav_positions_basic, transmit_power, bandwidth, area_size) for _ in range(total_time_slots)])
    average_energy_efficiency_padr = np.mean([evaluate_energy_efficiency(uav_positions_padr, transmit_power, bandwidth, area_size) for _ in range(total_time_slots)])
    average_energy_efficiency_adaptive = np.mean([evaluate_energy_efficiency(uav_positions_adaptive, transmit_power, bandwidth, area_size) for _ in range(total_time_slots)])
    
    improvement_ratio_energy_efficiency_padr = (average_energy_efficiency_padr - average_energy_efficiency_basic) / average_energy_efficiency_basic * 100
    improvement_ratio_energy_efficiency_adaptive = (average_energy_efficiency_adaptive - average_energy_efficiency_basic) / average_energy_efficiency_basic * 100
    
    return improvement_ratio_padr, improvement_ratio_adaptive, improvement_ratio_energy_efficiency_padr, improvement_ratio_energy_efficiency_adaptive, experiment_duration

# Запуск серии экспериментов
start_time_total = time.time()
results = Parallel(n_jobs=-1)(delayed(run_experiment)(seed) for seed in range(num_experiments))
end_time_total = time.time()

# Разделение результатов по приросту для PADR и Adaptive
improvement_ratios_padr, improvement_ratios_adaptive, improvement_ratios_energy_efficiency_padr, improvement_ratios_energy_efficiency_adaptive, experiment_durations = zip(*results)

# Вывод средних значений коэффициентов прироста и времени выполнения
mean_improvement_ratio_padr = np.mean(improvement_ratios_padr)
mean_improvement_ratio_adaptive = np.mean(improvement_ratios_adaptive)
mean_improvement_ratio_energy_efficiency_padr = np.mean(improvement_ratios_energy_efficiency_padr)
mean_improvement_ratio_energy_efficiency_adaptive = np.mean(improvement_ratios_energy_efficiency_adaptive)
mean_experiment_duration = np.mean(experiment_durations)

print(f'Average Improvement Ratio (PADR vs Basic): {mean_improvement_ratio_padr:.2f}%')
print(f'Average Improvement Ratio (Adaptive vs Basic): {mean_improvement_ratio_adaptive:.2f}%')
print(f'Average Improvement Ratio Energy Efficiency (PADR vs Basic): {mean_improvement_ratio_energy_efficiency_padr:.2f}%')
print(f'Average Improvement Ratio Energy Efficiency (Adaptive vs Basic): {mean_improvement_ratio_energy_efficiency_adaptive:.2f}%')
print(f'Average Experiment Duration: {mean_experiment_duration:.2f} seconds')
print(f'Total Execution Time: {end_time_total - start_time_total:.2f} seconds')