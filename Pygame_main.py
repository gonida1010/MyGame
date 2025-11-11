import pygame
import sys
import math
import random

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
        if char_type == 1:
            self.image = pygame.image.load('./images/red.png').convert_alpha()
        elif char_type == 2:
            self.image = pygame.image.load('./images/blue.png').convert_alpha()
        elif char_type == 3:
            self.image = pygame.image.load('./images/green.png').convert_alpha()
        else:  # (기본값) 또는 선택 오류 시 기본 픽셀로 된 이미지
            self.image = pygame.Surface((TILE_SIZE * 4, TILE_SIZE * 4))
            self.image.fill(color)

        # 이미지를 먼저 원하는 크기로 조절합니다.
        self.image = pygame.transform.scale(self.image, (TILE_SIZE * 8, TILE_SIZE * 8))

        self.rect = self.image.get_rect(center=(x, y))

        self.color = color
        self.controls = controls  # {'left': key, 'right': key, 'fire': key}
        self.char_type = char_type
        self.angle = 45  # 초기 발사 각도
        self.facing_right = True

        if self.char_type == 1:
            self.y_offset = -12  # 빨간색 캐릭터의 발 위치 오프셋
        elif self.char_type == 2:
            self.y_offset = -2  # 파란색 캐릭터의 발 위치 오프셋
        elif self.char_type == 3:
            self.y_offset = 10  # 초록색 캐릭터의 발 위치 오프셋
        else:
            self.y_offset = 0   # 기본 사각형 캐릭터의 오프셋

        # 넉백 기능 추가하기=> 중력을 위한 속도 변수 추가
        self.vel_x = 0.0
        self.vel_y = 0.0

    def update(self, terrain):
        # 넉백/관성으로 인한 x축 이동
        self.rect.x += int(self.vel_x)

        # x축 마찰력
        self.vel_x *= 0.9  # 매 프레임 속도 10% 감소
        if abs(self.vel_x) < 0.5:
            self.vel_x = 0

        # Y축 중력/속도 적용
        self.vel_y += GRAVITY
        self.rect.y += int(self.vel_y)
        
        # 바닥에 붙어있도록 조정
        while self.is_on_ground(terrain):
            self.rect.y -= 1
            self.vel_y = 0  # 땅에 닿았으니 수직 속도를 리셋하기

    def is_on_ground(self, terrain):
        # 플레이어가 땅에 있는지 확인하기
        # 플레이어 발밑 타일 확인
        # y_offset = 0
        feet_tile_x = self.rect.centerx // TILE_SIZE
        feet_tile_y = (self.rect.bottom + self.y_offset) // TILE_SIZE
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

    # 넉백 함수 추가하기(x,y 방향의 힘을 받도록 설정)
    def apply_knockback(self, kx, ky):
        self.vel_x += kx
        self.vel_y += ky


# 지형 클래스 만들기
class Terrain:
    def __init__(self):
        # 2D 배열로 맵 표현 (0: 빈 공간, 1: 흙)
        self.tiles = [[0 for _ in range(MAP_WIDTH)] for _ in range(MAP_HEIGHT)]
        # self.create_flat_map()

    # 맵 1번: 평평한 맵
    def create_map_1(self):
        print("Loding Map 1: 평원")
        map_level = MAP_HEIGHT * 3 // 4
        terrain_thickness = 25  # 땅 두께 타일 개수

        for y in range(map_level, map_level + terrain_thickness):
            if y >= MAP_HEIGHT: # 맵 높이를 벗어나지 않도록
                break
            
            for x in range(MAP_WIDTH // 5, MAP_WIDTH * 4 // 5):
                self.tiles[y][x] = 1


    def create_map_2(self):
        print("Loding Map 2: 구룽지")
        map_level = MAP_HEIGHT * 3 // 4
        terrain_thickness = 25  # 땅 두께 설정

        spawn_x_1 = (SCREEN_WIDTH // 4) // TILE_SIZE
        spawn_x_2 = (SCREEN_WIDTH * 3 // 4) // TILE_SIZE
        platform_width = 30 
        
        # [!!!] (수정) MAP_HEIGHT 대신 'map_level + terrain_thickness' 까지 루프
        for y in range(map_level, map_level + terrain_thickness):
            if y >= MAP_HEIGHT:
                break
            
            for x in range(MAP_WIDTH):
                # ... (이하 is_platform_area 로직은 동일) ...
                is_platform_area = False
                if x <= spawn_x_1 + platform_width // 2:
                    is_platform_area = True
                if x >= spawn_x_2 - platform_width // 2:
                    is_platform_area = True

                if is_platform_area:
                    self.tiles[y][x] = 1
                else:
                    self.tiles[y][x] = 0

    def create_map_3(self):
        print("Loding Map 3: 설원")
        base_level = MAP_HEIGHT * 3 // 4
        terrain_thickness = 25
        
        spawn_x_1 = (SCREEN_WIDTH // 4) // TILE_SIZE
        spawn_x_2 = (SCREEN_WIDTH * 3 // 4) // TILE_SIZE
        platform_width = 15

        for x in range(MAP_WIDTH):
            is_platform_area = False
            if spawn_x_1 - platform_width // 2 <= x <= spawn_x_1 + platform_width // 2:
                is_platform_area = True
            if spawn_x_2 - platform_width // 2 <= x <= spawn_x_2 + platform_width // 2:
                is_platform_area = True

            if is_platform_area:
                map_level = base_level
            else:
                hill_height = int(math.sin(x * 0.02) * (MAP_HEIGHT // 10))
                map_level = base_level - hill_height
            
            # [!!!] (수정) 이 안쪽 루프를 수정합니다.
            for y in range(map_level, map_level + terrain_thickness):
                if y >= MAP_HEIGHT:
                    break
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

        if char_type == 1:
            self.image = pygame.image.load('./images/투사체_불.png').convert_alpha()
        elif char_type == 2:
            self.image = pygame.image.load('./images/투사체_폭탄.png').convert_alpha()
        elif char_type == 3:
            self.image = pygame.image.load('./images/투사체_슬라임.png').convert_alpha()
        else:
            # 기본 발사체 이미지
            self.image = pygame.Surface((5, 5))
            self.image.fill(YELLOW)
        
        # 발사체 크기 수정
        self.image = pygame.transform.scale(self.image, (60, 60))
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

        # (추가) 그린 스킬을 위한 변수
        self.prev_vel_y = self.vel_y    # 이전 y속도 (정점 확인용)
        self.split_done = False         # 분리가 완료되었는지

    def update(self, terrain, players):
        new_projectiles = [] # (추가) 새로 생성될 발사체를 담을 리스트

        if not self.hit:
            # (추가) 그린 스킬 - 정점에서 분리 로직
            if self.char_type == 3 and self.bonus_shot and not self.split_done:
                # 1. 포물선의 정점(vel_y가 0을 지날 때)인지 확인
                if self.vel_y > 0 and self.prev_vel_y <= 0:
                    print("그린 스킬 발동!")
                    self.split_done = True # 한 번만 분리되도록

                    # 2. 3개의 새로운 '자식' 발사체 생성
                    # (char_type은 3, bonus_shot은 False로 줘서 자식이 또 분리되지 않게 함)
                    p1 = Projectile(self.x, self.y, 0, 3, False)
                    p1.vel_x = self.vel_x - 3   # 좌측
                    p1.vel_y = self.vel_y - 2   # 살짝 위로
                    p1.split_done = True        # 자식은 분리 안 함

                    p2 = Projectile(self.x, self.y, 0, 3, False)
                    p2.vel_x = self.vel_x       # 중앙
                    p2.vel_y = self.vel_y - 3   # 더 위로 (가운데가 높이)
                    p2.split_done = True
                    
                    p3 = Projectile(self.x, self.y, 0, 3, False)
                    p3.vel_x = self.vel_x + 3   # 우측
                    p3.vel_y = self.vel_y - 2   # 살짝 위로
                    p3.split_done = True

                    new_projectiles.extend([p1, p2, p3])

                    # 3. 원본(부모) 발사체는 제거
                    self.kill() 
                    return new_projectiles # 새 발사체 리스트를 반환하고 즉시 종료
            # --- (그린 스킬 로직 끝) ---

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
                    self.explode(terrain, players)
                    return new_projectiles

            # 화면 밖으로 나감 (낙사 아님, 그냥 소멸)
            if not (0 <= self.rect.centerx <= SCREEN_WIDTH and 0 <= self.rect.centery <= SCREEN_HEIGHT * 2):
                self.kill() # 스프라이트 그룹에서 제거

        self.prev_vel_y = self.vel_y
        return new_projectiles

    # 지형 파괴 속성 함수 만들기
    def explode(self, terrain, players):
        radius = 40 # 기본 반경
        
        # 캐릭터 2 (광역 폭발)
        if self.char_type == 2 and self.bonus_shot:
            radius = 70
        
        # 캐릭터 3 (3발 분산)
        if self.char_type == 3 and self.bonus_shot:
            pass
        
        terrain.destroy_terrain(self.rect.centerx, self.rect.centery, radius)

        # --- (넉백 로직 추가) ---
        knockback_radius = radius * 2  # 넉백 범위
        max_knockback_force = 8        # 최대 넉백 힘
        
        explosion_x, explosion_y = self.rect.center

        for player in players:
            # 1. 플레이어와 폭발 중심 사이의 거리 계산
            dist_x = player.rect.centerx - explosion_x
            dist_y = player.rect.centery - explosion_y
            distance = math.sqrt(dist_x**2 + dist_y**2)

            # 2. 넉백 범위 내에 있는지 확인 (0보다 커야 함)
            if 0 < distance < knockback_radius:
                # 3. 넉백 힘 계산 (거리에 반비례)
                force_magnitude = max_knockback_force * (1 - (distance / knockback_radius))
                
                # 4. 넉백 방향 (폭발 중심에서 플레이어 방향)
                knock_x = (dist_x / distance) * force_magnitude
                knock_y = (dist_y / distance) * force_magnitude
                
                # 5. (게임성 보정) Y축 넉백은 항상 위로 띄우기
                #    (아래로 박히는 넉백은 불쾌한 경험을 줄 수 있음)
                if knock_y > 0: # 아래로 향하는 넉백이라면
                    knock_y = -knock_y * 0.2 # 방향을 바꿔 약하게 위로 띄움
                
                # 6. (게임성 보정) 최소한의 수직 넉백을 보장 (위로 붕 뜨는 느낌)
                knock_y -= force_magnitude * 0.1

                # 7. 플레이어에게 넉백 적용
                player.apply_knockback(knock_x, knock_y)
        # --- (넉백 로직 끝) ---
        
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
        
        # 먼저 빈 지형 객체를 생성한다
        self.terrain = Terrain()

        # 랜덤으로 돌릴 맵들을 리스트로 저장하기
        map_choices = [
            {'bg': './images/평야배경.jpg', 'terrain_method': self.terrain.create_map_1},
            {'bg': './images/설원배경.jpg', 'terrain_method': self.terrain.create_map_2},
            {'bg': './images/우주하늘배경.jpg', 'terrain_method': self.terrain.create_map_3}
        ]

        # 저장한 리스트에 있는 맵들을 랜덤으로 선택하기
        chosen_map = random.choice(map_choices)
        # 선택된 맵의 배경 이미지를 로드하기
        try:
            self.background_image = pygame.image.load(chosen_map['bg']).convert()
            self.background_image = pygame.transform.scale(self.background_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
        except pygame.error as e:
            print(f"Error!! {chosen_map['bg']} 배경 이미지를 불러오지 못했습니다. {e}")
            self.background_image = None

        chosen_map['terrain_method']()

        # 플레이어 생성 (컨트롤, 캐릭터 타입 지정)
        player_1_controls = {'left': pygame.K_a, 'right': pygame.K_d, 'fire': pygame.K_SPACE}
        player_2_controls = {'left': pygame.K_LEFT, 'right': pygame.K_RIGHT, 'fire': pygame.K_RETURN} # Enter 키
        
        self.players = pygame.sprite.Group()

        self.player_list = [
            Player(SCREEN_WIDTH // 4, 
                   0,
                   RED, player_1_controls, char_type=1),
            Player(SCREEN_WIDTH * 3 // 4, 
                   0,
                   BLUE, player_2_controls, char_type=2)
        ]
        self.players.add(self.player_list)
        
        player_height = self.player_list[0].rect.height

        ground_y_center = (MAP_HEIGHT * 3 // 4) * TILE_SIZE - (player_height // 2)

        for player in self.player_list:
            player.rect.centery = ground_y_center

        self.projectiles = pygame.sprite.Group()
        
        self.turn_index = 0
        self.current_player = self.player_list[self.turn_index]
        self.game_state = "MOVE" # MOVE, AIM_1, AIM_2, FIRE, GAMEOVER
        
        self.state_timer = 0
        self.move_time_limit = 5000  # 5초 (밀리초)
        self.aim_2_time_limit = 3000 # 3초
        
        # 게이지 변수
        self.gauge_1_angle_speed = 2.4  # 1단계 게이지 속도임
        self.gauge_2_speed = (SCREEN_HEIGHT // 100) * 1.15 # 2단계 게이지 속도 설정
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
                self.multi_shot_counter = 0
                self.multi_shot_angle = 0
                print("Time over!")
                self.fire_projectile()
            else:
                # 2단계 게이지: 상하 이동
                self.gauge_2_value += self.gauge_2_speed * self.gauge_2_direction
                gauge_rect = pygame.Rect(SCREEN_WIDTH - 50, SCREEN_HEIGHT // 2 - 100, 20, 200)
                if self.gauge_2_value <= 0 or self.gauge_2_value >= gauge_rect.height:
                    self.gauge_2_direction *= -1

        elif self.game_state == "FIRE":
            if len(self.projectiles) == 0:
                # 1. 쏠 발사 횟수가 1발보다 많이 남았는지 확인
                if self.multi_shot_counter > 1:
                    print(f"연속 발사: {self.multi_shot_counter - 1}발 남음")
                    self.multi_shot_counter -= 1
                    # (딜레이를 살짝 주려면 여기에 타이머를 추가할 수 있음)
                    self.fire_single_projectile(self.multi_shot_angle)
                
                # 2. 쏠 발사 횟수가 1발(이거나 0발)이면 턴 종료
                else:
                    self.multi_shot_counter = 0 # 카운터 초기화
                    self.next_turn() # 턴 넘기기

        # 공통 업데이트
        self.players.update(self.terrain)
        self.projectiles.update(self.terrain, self.players)

        new_projectiles_list = []
        for proj in self.projectiles:
            # update가 새 발사체 리스트를 반환할 수 있음 (Green 스킬)
            new_projs = proj.update(self.terrain, self.players) 
            if new_projs:
                new_projectiles_list.extend(new_projs)
        
        # (루프가 끝난 후) 새로 생성된 발사체들을 메인 그룹에 추가
        if new_projectiles_list:
            self.projectiles.add(new_projectiles_list)
        
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
        
        # 1. 레드가 스킬을 쓴 경우
        if self.current_player.char_type == 1 and self.bonus_shot:
            print("레드 스킬 발동! 3발 연속 발사!")
            self.multi_shot_counter = 3  # (총 3발)
            self.multi_shot_angle = angle
            
            # (중요) 스킬 발동했으니 bonus_shot 플래그는 '사용'한 것으로 간주
            # self.bonus_shot = False # (이건 explode 수정을 보고 결정)

        # 2. 그 외 모든 경우 (일반 발사)
        else:
            self.multi_shot_counter = 1  # (총 1발)
            self.multi_shot_angle = angle

        # 3. 연속 발사든, 일반 발사든 [첫 번째 발]을 발사합니다.
        self.fire_single_projectile(self.multi_shot_angle)
        
    def fire_single_projectile(self, angle):
        """단일 발사체를 생성하고 그룹에 추가합니다."""
        proj = Projectile(self.current_player.rect.centerx, 
                          self.current_player.rect.centery, 
                          angle, 
                          self.current_player.char_type, 
                          self.bonus_shot) # bonus_shot 값은 넘겨주되...
        
        # bonus_shot이 스킬 발동 '여부'만 체크하도록,
        # Projectile 클래스에서는 이 값을 사용하지 않게 해야 함. (explode 수정 필요)
        
        self.projectiles.add(proj)



    def next_turn(self):
        self.turn_index = (self.turn_index + 1) % len(self.player_list)
        self.current_player = self.player_list[self.turn_index]
        self.game_state = "MOVE"
        self.state_timer = pygame.time.get_ticks() # 5초 이동 타이머 시작
        print(f"플레이어 {self.turn_index + 1} 턴 시작")

    # 화면에 출력되는 함수
    def draw(self):
        if self.background_image:
            self.surface.blit(self.background_image, (0, 0))
        else: # 이미지 로드 실패시 출력되는 화면 창
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