import pygame
import sys

def draw_start_button():
    pygame.draw.rect(screen, white, start_button)
    font = pygame.font.Font(None, 36)
    text = font.render("Start Game", True, bg_color)
    screen.blit(text, (width // 2 - 80, height // 2))

def game_started():
    for event in pygame.event.get():
        if event.type == pygame.MOUSEBUTTONDOWN:
            if start_button.collidepoint(event.pos):
                return True
        if event.type == pygame.QUIT:
            sys.exit()
    return False

def game_failed():
    if ball.bottom > height:
        return True
    return False

def reset_game():
    global ball, ball_speed, bricks, started
    ball = pygame.Rect(width // 2, height // 2, 20, 20)
    ball_speed = (2, 2)
    bricks = [pygame.Rect(pos, (brick_width, brick_height)) for pos in bricks_pos]
    started = False

def display_game_over():
    screen.fill(bg_color)
    font = pygame.font.Font(None, 36)
    text = font.render("Game Over", True, white)
    screen.blit(text, (width // 2 - 80, height // 2))
    pygame.display.flip()
    pygame.time.delay(2000)

# 초기 설정
pygame.init()
width, height = 800, 600
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Breakout Game")

# 색상 설정
bg_color = pygame.Color(0, 0, 0)
white = pygame.Color(255, 255, 255)

# 공 설정
ball_speed = (2, 2)
ball = pygame.Rect(width // 2, height // 2, 20, 20)

# 패들 설정
paddle_speed = 5
paddle = pygame.Rect(width // 2 - 50, height - 50, 100, 10)

# 벽돌 설정
brick_width, brick_height = 60, 20
brick_count_per_line = 10
brick_margin = 2
bricks_pos = [(idx % brick_count_per_line * (brick_width + brick_margin) + brick_margin,
              idx // brick_count_per_line * (brick_height + brick_margin) + brick_margin)
              for idx in range(brick_count_per_line * 3)]
bricks = [pygame.Rect(pos, (brick_width, brick_height)) for pos in bricks_pos]

# Start Button 설정
start_button = pygame.Rect(width // 2 - 100, height // 2, 200, 40)

started = False
game_over = False
while True:
    if not started:
        if game_over:
            display_game_over()
            game_over = False
        draw_start_button()
        pygame.display.flip()
        started = game_started()
        continue

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()

    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        paddle.move_ip(-paddle_speed, 0)
    if keys[pygame.K_RIGHT]:
        paddle.move_ip(paddle_speed, 0)

    ball.move_ip(ball_speed)
    if ball.left < 0 or ball.right > width:
        ball_speed = (-ball_speed[0], ball_speed[1])
    if ball.top < 0 or ball.colliderect(paddle):
        ball_speed = (ball_speed[0], -ball_speed[1])

    if game_failed():
        reset_game()
        game_over = True
        continue

    collided = ball.collidelist(bricks)
    if collided != -1:
        brick_rect = bricks.pop(collided)
        ball_speed = (ball_speed[0], -ball_speed[1])

    # 화면 업데이트
    screen.fill(bg_color)

    for brick in bricks:
        pygame.draw.rect(screen, white, brick)
    pygame.draw.rect(screen, white, paddle)
    pygame.draw.ellipse(screen, white, ball)
    pygame.draw.aaline(screen, white, (0, ball.top), (width, ball.top))

    pygame.display.flip()

    pygame.time.delay(10)