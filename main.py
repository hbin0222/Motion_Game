import pygame
import sys
import cv2
import numpy as np

#스타트 버튼 생성
def draw_start_button():
    pygame.draw.rect(screen, white, start_button)
    font = pygame.font.Font(None, 36)
    text = font.render("Start Game", True, bg_color)
    screen.blit(text, (width // 2 - 80, height // 2))
#게임 시작
def game_started():
    for event in pygame.event.get(): #발생한 모든 이벤트를 가져오기
        if event.type == pygame.MOUSEBUTTONDOWN: #이벤트가 마우스 클릭일 때
            if start_button.collidepoint(event.pos): #이벤트 발생 위치가 스타트버튼일 때 트루 반환
                return True
        if event.type == pygame.QUIT:
            sys.exit()
    return False
#게임 실패
def game_failed():
    if ball.bottom > height: 
        return True
    return False
#게임 초기화
def reset_game():
    global ball, ball_speed, bricks, started
    ball = pygame.Rect(width // 2, height // 2, 20, 20) #공의 출현위치와 크기를 지정
    ball_speed = (5, 5) #공이 움직이는 속도 가로, 세로 2픽셀
    bricks = [pygame.Rect(pos, (brick_width, brick_height)) for pos in bricks_pos] #벽돌 크기와 위치
    started = False
#게임종료
def display_game_over():
    screen.fill(bg_color)
    font = pygame.font.Font(None, 36)
    text = font.render("Game Over", True, white)
    screen.blit(text, (width // 2 - 80, height // 2))
    pygame.display.flip() #화면 전체를 업데이트
    pygame.time.delay(2000)

#생성
pygame.init()
width, height = 800, 600
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Breakout Game")

bg_color = pygame.Color(0, 0, 0) #배경 검정
white = pygame.Color(255, 255, 255)

ball_speed = (5, 3)
ball = pygame.Rect(width // 2, height // 2, 20, 20)

paddle_speed = 5
paddle = pygame.Rect(width // 2 - 50, height - 50, 100, 10)

brick_width, brick_height = 60, 20
brick_count_per_line = 13
brick_margin = 2
# 벽돌 좌표
bricks_pos = [(idx % brick_count_per_line * (brick_width + brick_margin) + brick_margin, # x좌표
              idx // brick_count_per_line * (brick_height + brick_margin) + brick_margin) # y좌표
              for idx in range(brick_count_per_line * 3)]
bricks = [pygame.Rect(pos, (brick_width, brick_height)) for pos in bricks_pos]

start_button = pygame.Rect(width // 2 - 100, height // 2, 200, 40)

cap = cv2.VideoCapture(1)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 700)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 200)

# 주먹 인식
hand_cascade = cv2.CascadeClassifier('hand.xml')

# OpenCV 윈도우 생성
cv2.namedWindow("Hand Detection")

started = False
game_over = False
while True:
    #카메라로부터 프레임을 읽어 옴
    ret, frame = cap.read()
    if not ret:
        break
    #좌우반전
    frame = cv2.flip(frame, 1)  # 1은 수평으로 반전합니다. 수직으로 반전하기 위해 -1을 사용할 수 있습니다.
    #손 인식을 위해 회색조 영상으로 변환
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    #인식률 조정
    hands = hand_cascade.detectMultiScale(gray, 1.5, 5)

    display_frame = frame.copy()

    for (x, y, w, h) in hands:
        paddle_center = x + (w // 2) - (paddle.width // 2)
        # 패들 위치 범위로 제한
        paddle.left = min(max(0, paddle_center-50), width - paddle.width)
        cv2.rectangle(display_frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
    #인식된 손 화면에 보여주기
    cv2.imshow("Hand Detection", display_frame)

    if not started:
        if game_over:
            display_game_over()
            game_over = False
        draw_start_button()
        pygame.display.flip()
        started = game_started()
        continue
    
    #닫기 창 누르면 시스템 종료
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()

    #패들 키보드로 수동 조정 부분
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        paddle.move_ip(-paddle_speed, 0)
    if keys[pygame.K_RIGHT]:
        paddle.move_ip(paddle_speed, 0)

    ball.move_ip(ball_speed)
    #공이 왼쪽벽과 오른쪽 벽에 부딪히면 x좌표를 바꾸어 반대로 이동
    if ball.left < 0 or ball.right > width:
        ball_speed = (-ball_speed[0], ball_speed[1])
    #공의 높이가 천장을 찍거나 패들과 충돌하면 y값을 바꾸어 위아래 이동
    if ball.top < 0 or ball.colliderect(paddle):
        ball_speed = (ball_speed[0], -ball_speed[1])

    if game_failed():
        reset_game()
        game_over = True
        continue
    #벽돌들 중에 충돌한 벽돌 식별; 없으면 -1 반환
    collided = ball.collidelist(bricks)
    #벽돌이 있다면
    if collided != -1:
        #해당 순번의 벽돌 삭제
        bricks.pop(collided)
        #공은 아래로 이동
        ball_speed = (ball_speed[0], -ball_speed[1])

    screen.fill(bg_color)

    #벽돌을 세팅
    for brick in bricks:
        pygame.draw.rect(screen, white, brick)
    #패들 세팅
    pygame.draw.rect(screen, white, paddle)
    #공 그리기
    pygame.draw.ellipse(screen, white, ball)

    # pygame.draw.aaline(screen, white, (0, ball.top), (width, ball.top))

    pygame.display.flip()

    pygame.time.delay(10)

cap.release()
cv2.destroyAllWindows()
pygame.quit()
