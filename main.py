import pygame
import sys
import cv2
import numpy as np

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

pygame.init()
width, height = 800, 600
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Breakout Game")

bg_color = pygame.Color(0, 0, 0)
white = pygame.Color(255, 255, 255)

ball_speed = (2, 2)
ball = pygame.Rect(width // 2, height // 2, 20, 20)

paddle_speed = 5
paddle = pygame.Rect(width // 2 - 50, height - 50, 100, 10)

brick_width, brick_height = 60, 20
brick_count_per_line = 10
brick_margin = 2
bricks_pos = [(idx % brick_count_per_line * (brick_width + brick_margin) + brick_margin,
              idx // brick_count_per_line * (brick_height + brick_margin) + brick_margin)
              for idx in range(brick_count_per_line * 3)]
bricks = [pygame.Rect(pos, (brick_width, brick_height)) for pos in bricks_pos]

start_button = pygame.Rect(width // 2 - 100, height // 2, 200, 40)

cap = cv2.VideoCapture(1)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 200)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 200)

hand_cascade = cv2.CascadeClassifier('hand.xml')

# OpenCV 윈도우 생성
cv2.namedWindow("Hand Detection")

started = False
game_over = False
while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)  # 1은 수평으로 반전합니다. 수직으로 반전하기 위해 -1을 사용할 수 있습니다.

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    hands = hand_cascade.detectMultiScale(gray, 1.3, 5)

    display_frame = frame.copy()

    for (x, y, w, h) in hands:
        paddle_center = x + (w // 2) - (paddle.width // 2)
        # 패들 위치 범위로 제한
        paddle.left = min(max(0, paddle_center), width - paddle.width)
        cv2.rectangle(display_frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

    cv2.imshow("Hand Detection", display_frame)

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
        bricks.pop(collided)
        ball_speed = (ball_speed[0], -ball_speed[1])

    screen.fill(bg_color)

    for brick in bricks:
        pygame.draw.rect(screen, white, brick)
    pygame.draw.rect(screen, white, paddle)
    pygame.draw.ellipse(screen, white, ball)
    pygame.draw.aaline(screen, white, (0, ball.top), (width, ball.top))

    pygame.display.flip()

    pygame.time.delay(10)

cap.release()
cv2.destroyAllWindows()
pygame.quit()
