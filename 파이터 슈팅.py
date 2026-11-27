
from tracemalloc import start

import pygame
import random
import sys
import time
import os


pygame.init()

# 화면 설정
WIDTH, HEIGHT = 600, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("전투기 슈팅 게임")

# 색상
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 50, 50)
GREEN = (50, 255, 50)
YELLOW = (255, 255, 0)
GRAY = (100, 100, 100)  

clock = pygame.time.Clock()
FPS = 60

font = pygame.font.SysFont("malgungothic", 24)
large_font = pygame.font.SysFont("malgungothic", 40)


# ==================================
# 전투기 이미지 불러오기
# ==================================

def load_fighter_image():
    image_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "fighter.png"
    )

    image = pygame.image.load(image_path).convert_alpha()

    # 흰색 배경 투명하게 만들기
    for x in range(image.get_width()):
        for y in range(image.get_height()):
            r, g, b, a = image.get_at((x, y))

            if r > 245 and g > 245 and b > 245:
                image.set_at((x, y), (255, 255, 255, 0))

    # 전투기 크기 조절
    image = pygame.transform.smoothscale(
        image, (100, 115)
    )

    return image


fighter_image = load_fighter_image()


# ==================================
# 플레이어 클래스
# ==================================

class Player(pygame.sprite.Sprite):

    def __init__(self):
        super().__init__()

        self.image = fighter_image
        self.rect = self.image.get_rect()

        self.rect.centerx = WIDTH // 2
        self.rect.bottom = HEIGHT - 20

        self.speed = 6
        self.hp = 5

    def update(self):

        keys = pygame.key.get_pressed()

        if keys[pygame.K_LEFT]:
            self.rect.x -= self.speed

        if keys[pygame.K_RIGHT]:
            self.rect.x += self.speed

        if keys[pygame.K_UP]:
            self.rect.y -= self.speed

        if keys[pygame.K_DOWN]:
            self.rect.y += self.speed

        # 화면 밖으로 나가지 않도록 설정
        self.rect.clamp_ip(screen.get_rect())


# ==================================
# 미사일 클래스
# ==================================

class Bullet(pygame.sprite.Sprite):

    def __init__(self, x, y):
        super().__init__()

        self.image = pygame.Surface((6, 18))
        self.image.fill(YELLOW)

        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y

        self.speed = -10

    def update(self):

        self.rect.y += self.speed

        if self.rect.bottom < 0:
            self.kill()


# ==================================
# 적 클래스
# ==================================

class Enemy(pygame.sprite.Sprite):

    def __init__(self):
        super().__init__()

        self.image = pygame.Surface((35, 35))
        self.image.fill(RED)

        self.rect = self.image.get_rect()

        self.reset()

    def reset(self):

        self.rect.x = random.randint(
            0, WIDTH - self.rect.width
        )

        self.rect.y = random.randint(-150, -40)

        self.speed = random.randint(3, 6)

    def update(self):

        self.rect.y += self.speed

        if self.rect.top > HEIGHT:
            self.reset()


# ==================================
# 스프라이트 그룹
# ==================================

all_sprites = pygame.sprite.Group()
enemies = pygame.sprite.Group()
bullets = pygame.sprite.Group()

player = Player()

all_sprites.add(player)

# 적 7마리 생성
for _ in range(7):

    enemy = Enemy()

    all_sprites.add(enemy)
    enemies.add(enemy)


# ==================================
# 게임 변수
# ==================================

score = 0

last_kill_time = 0

combo_active = False

running = True
game_over = False


# ==================================
# 일시정지 메뉴
# ==================================

def show_pause_menu():

    paused = True

    while paused:

        screen.fill(BLACK)

        pause_text = large_font.render(
            "PAUSED", True, WHITE
        )

        screen.blit(
            pause_text,
            (WIDTH // 2 - 75, HEIGHT // 3)
        )

        button_rect = pygame.Rect(
            WIDTH // 2 - 90,
            HEIGHT // 2,
            180,
            55
        )

        pygame.draw.rect(
            screen, GRAY, button_rect
        )

        btn_text = font.render(
            "게임 종료", True, WHITE
        )

        screen.blit(
            btn_text,
            (WIDTH // 2 - 48, HEIGHT // 2 + 12)
        )

        pygame.display.flip()

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_ESCAPE:
                    paused = False

            if event.type == pygame.MOUSEBUTTONDOWN:

                if button_rect.collidepoint(event.pos):
                    pygame.quit()
                    sys.exit()


# ==================================
# 메인 게임 루프
# ==================================

while running:

    clock.tick(FPS)

    current_time = time.time()

    # 이벤트 처리
    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_ESCAPE:
                show_pause_menu()

            # 스페이스바로 미사일 발사
            if event.key == pygame.K_SPACE and not game_over:

                bullet = Bullet(
                    player.rect.centerx,
                    player.rect.top
                )

                all_sprites.add(bullet)
                bullets.add(bullet)

    if not game_over:

        # 모든 스프라이트 업데이트
        all_sprites.update()

        # 콤보 시간 확인
        if current_time - last_kill_time > 5:
            combo_active = False

        # 미사일과 적 충돌
        hits = pygame.sprite.groupcollide(
            enemies,
            bullets,
            True,
            True
        )

        for hit in hits:

            if current_time - last_kill_time <= 5:
                score += 20
                combo_active = True

            else:
                score += 10
                combo_active = False

            last_kill_time = time.time()

            # 새로운 적 생성
            new_enemy = Enemy()

            all_sprites.add(new_enemy)
            enemies.add(new_enemy)

        # 플레이어와 적 충돌
        player_hits = pygame.sprite.spritecollide(
            player,
            enemies,
            True
        )

        for hit in player_hits:

            player.hp -= 1

            new_enemy = Enemy()

            all_sprites.add(new_enemy)
            enemies.add(new_enemy)

            if player.hp <= 0:
                game_over = True

    # ==================================
    # 화면 그리기
    # ==================================

    screen.fill(BLACK)

    # 별 배경
    # 게임 시작 시 생성된 별 위치 사용
    
# 별 배경
for x, y in start:
    pygame.draw.circle(screen, WHITE, (x, y), 1)



    

    # 스프라이트 그리기
    all_sprites.draw(screen)

    # 점수 표시
    score_text = font.render(
        f"점수: {score}", True, WHITE
    )

    screen.blit(score_text, (10, 10))

    # 체력 표시
    hp_text = font.render(
        "체력:", True, WHITE
    )

    screen.blit(hp_text, (10, 40))

    for i in range(player.hp):

        pygame.draw.rect(
            screen,
            GREEN,
            (85 + i * 25, 45, 20, 15)
        )

    # 콤보 표시
    if combo_active and current_time - last_kill_time <= 5:

        combo_text = font.render(
            "★ DOUBLE SCORE BONUS! ★",
            True,
            YELLOW
        )

        screen.blit(
            combo_text,
            (WIDTH // 2 - 145, 10)
        )

    # 게임 오버
    if game_over:

        over_text = large_font.render(
            "GAME OVER", True, RED
        )

        screen.blit(
            over_text,
            (WIDTH // 2 - 115, HEIGHT // 2 - 30)
        )

        final_score = font.render(
            f"최종 점수: {score}",
            True,
            WHITE
        )

        screen.blit(
            final_score,
            (WIDTH // 2 - 75, HEIGHT // 2 + 25)
        )

    pygame.display.flip()


pygame.quit()
sys.exit()
