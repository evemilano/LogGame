import pygame
import threading
import paramiko
import time
import re
import os
import random

#from config import LOG_FILE, ip, user, keys_folder
log_file ='/var/log/nginx/evemilano_access.log'
ip = '134.209.236.203'
user = 'root'
keys_folder = "/home/gioz/Desktop/python/pylog/keys"

# Inizializzazione di Pygame
pygame.init()
# Configurazioni e Definizioni Variabili

WIDTH, HEIGHT = 700, 500
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
RED = (255, 0, 0)
LIGHT_BLUE = (173, 216, 230)

#screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
#WIDTH, HEIGHT = screen.get_size()
SERVER_POS = (WIDTH // 2, HEIGHT // 2)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Web Server Log Monitor Game")

# Lista per le richieste
requests = []
clients = {}

class Client:
    def __init__(self, ip):
        self.ip = ip
        self.client_pos = (random.randint(0, WIDTH), random.randint(0, HEIGHT))
        self.requests = []

    def add_request(self, request):
        self.requests.append(request)

    def remove_request(self, request):
        self.requests.remove(request)

    def is_active(self):
        return len(self.requests) > 0

class Request:
    def __init__(self, client, status_code, resource):
        self.client = client
        self.server_pos = SERVER_POS
        self.progress = 0.0
        self.response_sent = False
        self.status_code = status_code
        self.resource = resource
        self.response_color = self.get_response_color()

    def get_response_color(self):
        if 200 <= self.status_code < 300:
            return GREEN
        elif 300 <= self.status_code < 400:
            return YELLOW
        elif 400 <= self.status_code < 500:
            return None  # No response line for 4xx errors
        elif 500 <= self.status_code < 600:
            return None  # No response line for 5xx errors

    def update(self, dt):
        if not self.response_sent:
            self.progress += dt * 1.4  # VelocitÃ  di andata raddoppiata
            if self.progress >= 1.0:
                self.progress = 1.0
                self.response_sent = True
        else:
            self.progress -= dt * 1.4  # VelocitÃ  di ritorno raddoppiata
            if self.progress <= 0.0:
                self.client.remove_request(self)
                requests.remove(self)

    def draw(self, screen):
        client_to_server = (
            self.client.client_pos[0] + (self.server_pos[0] - self.client.client_pos[0]) * self.progress,
            self.client.client_pos[1] + (self.server_pos[1] - self.client.client_pos[1]) * self.progress,
        )
        pygame.draw.line(screen, BLUE, self.client.client_pos, client_to_server, 4)  # Spessore raddoppiato
        if self.response_sent and self.response_color:
            pygame.draw.line(screen, self.response_color, self.server_pos, client_to_server, 4)  # Spessore raddoppiato
        if not self.response_sent:
            font = pygame.font.Font(None, 24)
            #text_surface = font.render(self.resource, True, LIGHT_BLUE)
            text_surface = font.render(self.client.ip, True, LIGHT_BLUE)

            screen.blit(text_surface, (self.client.client_pos[0] - text_surface.get_width() // 2, self.client.client_pos[1] + 10))
        #print(f"Drawing request: {self.client.client_pos}, progress: {self.progress}, response_sent: {self.response_sent}")

def find_correct_ssh_key(ip, user, keys_folder):
    keys = [os.path.join(keys_folder, key) for key in os.listdir(keys_folder)]
    for key in keys:
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(ip, username=user, key_filename=key)
            print(f"SSH connection OK with key {key}")  
            ssh.close()
            return key
        
        except Exception as e:
            print(f"SSH connection failed with key {key}: {e}")  # Aggiunto per il debug
            continue
    return None

def monitor_log(ip, user, key_filename, log_file):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(ip, username=user, key_filename=key_filename)
    print(f'opening {log_file}')
    command = f"tail -f {log_file}"
    stdin, stdout, stderr = ssh.exec_command(command)

    log_pattern = re.compile(r'(\d+\.\d+\.\d+\.\d+) - - \[.*?\] ".*? (.*?) HTTP.*?" (\d{3})')  # Pattern per catturare l'IP del client, la risorsa richiesta e lo status code
    while True:
        line = stdout.readline()
        if line:
            print(f"Log line read: {line.strip()}")  # Debug output
            match = log_pattern.search(line)
            if match:
                client_ip = match.group(1)
                resource = match.group(2)
                status_code = int(match.group(3))
                print(f"Client IP matched: {client_ip}, Status code: {status_code}, Resource: {resource}")  # Debug output

                if client_ip not in clients:
                    clients[client_ip] = Client(client_ip)

                client = clients[client_ip]
                request = Request(client, status_code, resource)
                client.add_request(request)
                requests.append(request)

                print(f"Request added at position: {client.client_pos} with status code: {status_code}")

                if 400 <= status_code < 500:
                    flash_server(ORANGE)
                elif 500 <= status_code < 600:
                    flash_server(RED)
        else:
            time.sleep(0.1)  # Aggiunto per evitare di consumare CPU

def flash_server(color, duration=0.5):
    global server_flash_color, server_flash_end_time
    server_flash_color = color
    server_flash_end_time = time.time() + duration


correct_key = find_correct_ssh_key(ip, user, keys_folder)
if correct_key:
    log_thread = threading.Thread(target=monitor_log, args=(ip, user, correct_key, log_file))
    log_thread.daemon = True
    log_thread.start()
else:
    print("Nessuna chiave ha permesso l'accesso al server remoto.")
    exit(1)

# Loop principale del gioco
running = True
clock = pygame.time.Clock()
server_flash_color = LIGHT_BLUE
server_flash_end_time = 0

while running:
    dt = clock.tick(60) / 1000.0  # Delta time in seconds

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill(BLACK)  # Cambia il colore di sfondo a nero

    # Cambia il colore del server se necessario
    if time.time() < server_flash_end_time:
        pygame.draw.circle(screen, server_flash_color, SERVER_POS, 20)
    else:
        pygame.draw.circle(screen, LIGHT_BLUE, SERVER_POS, 20)

    #print(f"Number of requests: {len(requests)}")  # Stampa il numero di richieste

    for client in clients.values():
        if client.is_active():
            pygame.draw.circle(screen, LIGHT_BLUE, client.client_pos, 5)

    for req in requests:
        req.update(dt)
        req.draw(screen)

    pygame.display.flip()

pygame.quit()
