import pygame
import sys
import math

# 기본 상수 설정(고정될 값은 대문자로 표현하기)
# 기본 게임 화면 설정
SCREEN_WIDTH = 1280  
SCREEN_HEIGHT = 720  
FPS = 60
GRAVITY = 0.1  # 중력세기 테스트중
PROJECTILE_VELOCITY = 8  # 발사 세기 (고정)

# 임시 색상 설정
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 50, 50)
BLUE = (50, 50, 255)
GREEN = (50, 255, 50)
YELLOW = (255, 255, 0)
GRAY = (100, 100, 100)
SKY_BLUE = (135, 206, 235)

# 타일 설정
TILE_SIZE = 5  # 맵 타일 크기
MAP_WIDTH = SCREEN_WIDTH // TILE_SIZE
MAP_HEIGHT = SCREEN_HEIGHT // TILE_SIZE

# 플레이어 클래스 설정
class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, color, controls, char_type=1):
        super().__init__()
        self.image = pygame.Surface((TILE_SIZE * 4, TILE_SIZE * 4))
        self.image.fill(color)
        self.rect = self.image.get_rect(center=(x, y))
        self.color = color
        self.controls = controls  # {'left': key, 'right': key, 'fire': key}
        self.char_type = char_type
        self.angle = 45  # 초기 발사 각도
        self.facing_right = True

    def update(self, terrain):
        # 중력 적용 (간단화된 버전)
        if not self.is_on_ground(terrain):
            self.rect.y += TILE_SIZE // 2
        
        # 바닥에 붙어있도록 조정
        while self.is_on_ground(terrain):
            self.rect.y -= 1
        self.rect.y += 1 # 다시 한 칸 내리기

    def is_on_ground(self, terrain):
        # 플레이어가 땅에 있는지 확인하기
        # 플레이어 발밑 타일 확인
        feet_tile_x = self.rect.centerx // TILE_SIZE
        feet_tile_y = (self.rect.bottom + 1) // TILE_SIZE
        if 0 <= feet_tile_x < MAP_WIDTH and 0 <= feet_tile_y < MAP_HEIGHT:
            return terrain.tiles[feet_tile_y][feet_tile_x] == 1
        return False

    # 좌우 이동 함수 만들기
    def move(self, dx, terrain):
        new_x = self.rect.x + dx
        
        # 화면 밖으로 나가지 않도록 입력하기
        if 0 <= new_x and new_x + self.rect.width <= SCREEN_WIDTH:
            self.rect.x = new_x
            if dx > 0:
                self.facing_right = True
            elif dx < 0:
                self.facing_right = False
        
        # TODO: 지형 충돌 로직 추가 필요

    def draw_aim_indicator(self, surface):
        # 현재 각도로 조준선 그리기
        length = 50
        angle_rad = math.radians(self.angle if self.facing_right else 180 - self.angle)
        end_x = self.rect.centerx + length * math.cos(angle_rad)
        end_y = self.rect.centery - length * math.sin(angle_rad)
        pygame.draw.line(surface, self.color, self.rect.center, (end_x, end_y), 3)

# 지형 클래스 만들기
class Terrain:
    def __init__(self):
        # 2D 배열로 맵 표현 (0: 빈 공간, 1: 흙)
        self.tiles = [[0 for _ in range(MAP_WIDTH)] for _ in range(MAP_HEIGHT)]
        self.create_flat_map()

    def create_flat_map(self):
        # 평평한 맵 설정하기
        map_level = MAP_HEIGHT * 3 // 4
        for y in range(map_level, MAP_HEIGHT):
            for x in range(MAP_WIDTH // 5, MAP_WIDTH * 4 // 5):
                self.tiles[y][x] = 1

    def draw(self, surface):
        # 지형 그리기
        for y, row in enumerate(self.tiles):
            for x, tile in enumerate(row):
                if tile == 1:
                    rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                    pygame.draw.rect(surface, GRAY, rect)

    def destroy_terrain(self, x, y, radius):
        # x, y 축의 지형을 파괴하기
        tile_x, tile_y = x // TILE_SIZE, y // TILE_SIZE
        tile_radius = radius // TILE_SIZE

        for r_y in range(-tile_radius, tile_radius + 1):
            for r_x in range(-tile_radius, tile_radius + 1):
                # 원 모양으로 파괴하기
                if r_x*r_x + r_y*r_y <= tile_radius*tile_radius:
                    check_x, check_y = tile_x + r_x, tile_y + r_y
                    if 0 <= check_x < MAP_WIDTH and 0 <= check_y < MAP_HEIGHT:
                        self.tiles[check_y][check_x] = 0

# 발사체 클래스 만들기
class Projectile(pygame.sprite.Sprite):
    def __init__(self, x, y, angle, char_type, bonus_shot):
        super().__init__()
        self.image = pygame.Surface((5, 5))
        self.image.fill(YELLOW)
        self.rect = self.image.get_rect(center=(x, y))
        
        self.x = float(x)
        self.y = float(y)
        self.angle_rad = math.radians(angle)
        
        self.vel_x = PROJECTILE_VELOCITY * math.cos(self.angle_rad)
        self.vel_y = -PROJECTILE_VELOCITY * math.sin(self.angle_rad)
        
        self.char_type = char_type
        self.bonus_shot = bonus_shot
        self.particles = [] # 궤적용
        self.hit = False

    def update(self, terrain):
        if not self.hit:
            self.vel_y += GRAVITY
            self.x += self.vel_x
            self.y += self.vel_y
            self.rect.center = (round(self.x), round(self.y))
            
            self.particles.append(self.rect.center)
            if len(self.particles) > 50:
                self.particles.pop(0)

            # 지형 충돌 확인
            tile_x = self.rect.centerx // TILE_SIZE
            tile_y = self.rect.centery // TILE_SIZE
            
            if 0 <= tile_x < MAP_WIDTH and 0 <= tile_y < MAP_HEIGHT:
                if terrain.tiles[tile_y][tile_x] == 1:
                    self.hit = True
                    self.explode(terrain)

            # 화면 밖으로 나감 (낙사 아님, 그냥 소멸)
            if not (0 <= self.rect.centerx <= SCREEN_WIDTH and 0 <= self.rect.centery <= SCREEN_HEIGHT * 2):
                self.kill() # 스프라이트 그룹에서 제거

    # 지형 파괴 속성 함수 만들기
    def explode(self, terrain):
        radius = 30 # 기본 반경
        
        # 캐릭터 2 (광역 폭발)
        if self.char_type == 2 and self.bonus_shot:
            radius = 50
        
        # 캐릭터 1 (3발 집중) - 여기서는 파괴 반경으로 대체
        if self.char_type == 1 and self.bonus_shot:
            terrain.destroy_terrain(self.rect.centerx, self.rect.centery, radius)
            terrain.destroy_terrain(self.rect.centerx + 10, self.rect.centery, radius)
            terrain.destroy_terrain(self.rect.centerx - 10, self.rect.centery, radius)
        
        # 캐릭터 3 (3발 분산)
        elif self.char_type == 3 and self.bonus_shot:
            terrain.destroy_terrain(self.rect.centerx, self.rect.centery, radius)
            terrain.destroy_terrain(self.rect.centerx + 40, self.rect.centery, radius // 2)
            terrain.destroy_terrain(self.rect.centerx - 40, self.rect.centery, radius // 2)
        else:
            # 기본 1발
            terrain.destroy_terrain(self.rect.centerx, self.rect.centery, radius)
        
        # TODO: 폭발 시 플레이어 넉백(밀어내기) 로직 추가
        
        self.kill() # 충돌 후 제거

    def draw(self, surface):
        # 궤적 그리기
        for point in self.particles:
            pygame.draw.circle(surface, YELLOW, point, 1)
        surface.blit(self.image, self.rect)

# 메인 게임 로직 클래스 설정
class Game:
    def __init__(self, surface):
        self.surface = surface
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 36)
        
        self.terrain = Terrain()
        
        # 플레이어 생성 (컨트롤, 캐릭터 타입 지정)
        player_1_controls = {'left': pygame.K_a, 'right': pygame.K_d, 'fire': pygame.K_SPACE}
        player_2_controls = {'left': pygame.K_LEFT, 'right': pygame.K_RIGHT, 'fire': pygame.K_RETURN} # Enter 키
        
        self.players = pygame.sprite.Group()
        self.player_list = [
            Player(SCREEN_WIDTH // 4, SCREEN_HEIGHT // 2, RED, player_1_controls, char_type=1),
            Player(SCREEN_WIDTH * 3 // 4, SCREEN_HEIGHT // 2, BLUE, player_2_controls, char_type=2)
        ]
        self.players.add(self.player_list)
        
        self.projectiles = pygame.sprite.Group()
        
        self.turn_index = 0
        self.current_player = self.player_list[self.turn_index]
        self.game_state = "MOVE" # MOVE, AIM_1, AIM_2, FIRE, GAMEOVER
        
        self.state_timer = 0
        self.move_time_limit = 5000  # 5초 (밀리초)
        self.aim_2_time_limit = 3000 # 3초
        
        # 게이지 변수
        self.gauge_1_angle_speed = 2.2
        self.gauge_2_speed = (SCREEN_HEIGHT // 100) * 1.15 # 2배속 (1단계 게이지는 각도라 속도 비교가 다름)
        self.gauge_2_value = 0
        self.gauge_2_direction = 1
        self.gauge_2_target_y = 0
        self.gauge_2_target_height = 20
        self.bonus_shot = False

    def run(self):
        while True:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)

    def handle_events(self):
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # --- 상태별 키 입력 처리 ---
            keys = pygame.key.get_pressed()
            
            # [1. 이동 상태]
            if self.game_state == "MOVE":
                if keys[self.current_player.controls['left']]:
                    self.current_player.move(-5, self.terrain)
                if keys[self.current_player.controls['right']]:
                    self.current_player.move(5, self.terrain)
            
            # [2. 조준 1단계 (각도) 상태]
            elif self.game_state == "AIM_1":
                if event.type == pygame.KEYDOWN and event.key == self.current_player.controls['fire']:
                    # 1단계 게이지 완료 -> 2단계로
                    self.game_state = "AIM_2"
                    self.state_timer = pygame.time.get_ticks() # 3초 타이머 시작
                    self.gauge_2_value = 0
                    self.gauge_2_direction = 1
                    # 랜덤한 타겟 위치 설정
                    self.gauge_2_target_y = pygame.Rect(0, 0, 20, self.gauge_2_target_height).centery + (SCREEN_HEIGHT // 2 - 100) + (180 * (pygame.time.get_ticks() % 1000 / 1000.0))
            
            # [3. 조준 2단계 (보너스) 상태]
            elif self.game_state == "AIM_2":
                if event.type == pygame.KEYDOWN and event.key == self.current_player.controls['fire']:
                    # 2단계 게이지 발사!
                    gauge_rect = pygame.Rect(SCREEN_WIDTH - 50, SCREEN_HEIGHT // 2 - 100, 20, 200)
                    target_rect = pygame.Rect(gauge_rect.x, self.gauge_2_target_y, gauge_rect.width, self.gauge_2_target_height)
                    indicator_rect = pygame.Rect(gauge_rect.x, gauge_rect.y + self.gauge_2_value, gauge_rect.width, 5)

                    # 성공 판정
                    if target_rect.colliderect(indicator_rect):
                        self.bonus_shot = True
                        print("SKILL SHOT!")
                    else:
                        self.bonus_shot = False
                        print("실패!")
                    
                    self.fire_projectile()
            
    def update(self):
        current_time = pygame.time.get_ticks()
        
        # 상태별 업데이트 로직
        if self.game_state == "MOVE":
            if current_time - self.state_timer > self.move_time_limit:
                # 5초 이동 시간 종료 -> 조준 1단계 시작
                self.game_state = "AIM_1"
                self.current_player.angle = 45 # 각도 초기화

        elif self.game_state == "AIM_1":
            # 1단계 게이지: 각도 조절
            self.current_player.angle += self.gauge_1_angle_speed
            if self.current_player.angle > 180 or self.current_player.angle < 0:
                self.gauge_1_angle_speed *= -1

        elif self.game_state == "AIM_2":
            # 3초 시간 초과 시 실패하고 1발만 발사
            if current_time - self.state_timer > self.aim_2_time_limit:
                self.bonus_shot = False
                print("2단계 조준 시간 초과!")
                self.fire_projectile()
            else:
                # 2단계 게이지: 상하 이동
                self.gauge_2_value += self.gauge_2_speed * self.gauge_2_direction
                gauge_rect = pygame.Rect(SCREEN_WIDTH - 50, SCREEN_HEIGHT // 2 - 100, 20, 200)
                if self.gauge_2_value <= 0 or self.gauge_2_value >= gauge_rect.height:
                    self.gauge_2_direction *= -1

        elif self.game_state == "FIRE":
            if len(self.projectiles) == 0:
                # 모든 발사체가 사라지면 턴 변경
                self.next_turn()

        # 공통 업데이트
        self.players.update(self.terrain)
        self.projectiles.update(self.terrain)
        
        # 낙사(승리) 조건 확인
        for player in self.player_list:
            if player.rect.top > SCREEN_HEIGHT:
                self.game_state = "GAMEOVER"
                self.winner = self.player_list[1 - self.player_list.index(player)] # 상대방이 승리
                print(f"{self.winner.color} 승리!")

    def fire_projectile(self):
        self.game_state = "FIRE"
        
        angle = self.current_player.angle
        if not self.current_player.facing_right:
            angle = 180 - angle

        proj = Projectile(self.current_player.rect.centerx, 
                          self.current_player.rect.centery, 
                          angle, 
                          self.current_player.char_type, 
                          self.bonus_shot)
        self.projectiles.add(proj)
        
        # 캐릭터 1 (3발 집중) - TODO: 실제 3발 발사 로직으로 변경 필요
        # 현재는 Projectile 클래스의 explode에서 처리하고 있음
        
    def next_turn(self):
        self.turn_index = (self.turn_index + 1) % len(self.player_list)
        self.current_player = self.player_list[self.turn_index]
        self.game_state = "MOVE"
        self.state_timer = pygame.time.get_ticks() # 5초 이동 타이머 시작
        print(f"플레이어 {self.turn_index + 1} 턴 시작")

    def draw(self):
        # 모든 것을 화면에 출력하기
        self.surface.fill(SKY_BLUE)
        
        # 지형 그리기
        self.terrain.draw(self.surface)
        
        # 플레이어 그리기
        self.players.draw(self.surface)
        self.current_player.draw_aim_indicator(self.surface) # 현재 플레이어 조준선
        
        # 발사체 및 궤적 그리기
        for proj in self.projectiles:
            proj.draw(self.surface)

        # UI 그리기
        turn_text = self.font.render(f"Player {self.turn_index + 1}'s Turn", True, self.current_player.color)
        self.surface.blit(turn_text, (SCREEN_WIDTH // 2 - turn_text.get_width() // 2, 10))
        
        state_text = self.font.render(f"State: {self.game_state}", True, WHITE)
        self.surface.blit(state_text, (10, 10))

        # [1. 이동 상태 UI]
        if self.game_state == "MOVE":
            remaining_time = (self.move_time_limit - (pygame.time.get_ticks() - self.state_timer)) / 1000.0
            time_text = self.font.render(f"Move: {remaining_time:.1f}s", True, WHITE)
            self.surface.blit(time_text, (self.current_player.rect.centerx - 30, self.current_player.rect.top - 40))

        # [2. 조준 1단계 UI (각도)]
        elif self.game_state == "AIM_1":
            angle_text = self.font.render(f"Angle: {self.current_player.angle:.0f}", True, WHITE)
            self.surface.blit(angle_text, (self.current_player.rect.centerx - 30, self.current_player.rect.top - 40))
            # (UI는 draw_aim_indicator가 대체)

        # [3. 조준 2단계 UI (보너스 샷)]
        elif self.game_state == "AIM_2":
            # 3초 타이머
            remaining_time = (self.aim_2_time_limit - (pygame.time.get_ticks() - self.state_timer)) / 1000.0
            time_text = self.font.render(f"BONUS: {remaining_time:.1f}s", True, RED)
            self.surface.blit(time_text, (SCREEN_WIDTH // 2 - time_text.get_width() // 2, 50))
            
            # 2단계 게이지 바
            gauge_rect = pygame.Rect(SCREEN_WIDTH - 50, SCREEN_HEIGHT // 2 - 100, 20, 200)
            pygame.draw.rect(self.surface, BLACK, gauge_rect)
            
            # 랜덤 타겟
            target_rect = pygame.Rect(gauge_rect.x, self.gauge_2_target_y, gauge_rect.width, self.gauge_2_target_height)
            pygame.draw.rect(self.surface, GREEN, target_rect)
            
            # 현재 위치 표시
            indicator_rect = pygame.Rect(gauge_rect.x, gauge_rect.y + self.gauge_2_value, gauge_rect.width, 5)
            pygame.draw.rect(self.surface, YELLOW, indicator_rect)

        elif self.game_state == "GAMEOVER":
            win_text = self.font.render(f"Player {self.player_list.index(self.winner) + 1} WINS!", True, self.winner.color, BLACK)
            self.surface.blit(win_text, (SCREEN_WIDTH // 2 - win_text.get_width() // 2, SCREEN_HEIGHT // 2 - win_text.get_height() // 2))

        pygame.display.flip()

# 게임 시작
if __name__ == "__main__":
    pygame.init()
    pygame.font.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Artillery Knock-off Game Prototype")
    
    game = Game(screen)
    game.run()