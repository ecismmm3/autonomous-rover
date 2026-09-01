import RPi.GPIO as GPIO
import time
import math
import pygame
import smbus2
import os
import sys
import tty
import termios
import threading

# DISPLAY

os.environ['SDL_VIDEODRIVER'] = 'x11'
os.environ['DISPLAY'] = ':0'

GPIO.cleanup()
GPIO.setmode(GPIO.BCM)

# ultrasonic sensor setup
TRIG = 23
ECHO = 24
GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)

# servo setup
SERVO_PIN = 18
GPIO.setup(SERVO_PIN, GPIO.OUT)
servo_pwm = GPIO.PWM(SERVO_PIN, 50)
servo_pwm.start(0)

# motor pins
ENA1, IN1, IN2 = 26, 6, 25
ENB1, IN3, IN4 = 19, 16, 20
ENA2, IN5, IN6 = 12, 17, 27
ENB2, IN7, IN8 = 13, 22, 5

for pin in [ENA1, IN1, IN2, ENB1, IN3, IN4, ENA2, IN5, IN6, ENB2, IN7, IN8]:
    GPIO.setup(pin, GPIO.OUT)

pwm_a1 = GPIO.PWM(ENA1, 1000)
pwm_b1 = GPIO.PWM(ENB1, 1000)
pwm_a2 = GPIO.PWM(ENA2, 1000)
pwm_b2 = GPIO.PWM(ENB2, 1000)

for pwm in [pwm_a1, pwm_b1, pwm_a2, pwm_b2]:
    pwm.start(0)


SPEED         = 75
SAFE_DISTANCE = 20.0   # cm
MIN_ANGLE     = 0.0
MAX_ANGLE     = 120.0
STEP          = 2.0
SERVO_INTERVAL= 0.05
running       = True


distance      = 999.0
distance_lock = threading.Lock()
servo_pos     = 0.0
servo_dir     = 1


def front_leftf(speed):
    GPIO.output(IN1, GPIO.HIGH); GPIO.output(IN2, GPIO.LOW)
    pwm_a1.ChangeDutyCycle(speed)

def front_leftb(speed):
    GPIO.output(IN1, GPIO.LOW); GPIO.output(IN2, GPIO.HIGH)
    pwm_a1.ChangeDutyCycle(speed)

def front_lefts():
    GPIO.output(IN1, GPIO.LOW); GPIO.output(IN2, GPIO.LOW)
    pwm_a1.ChangeDutyCycle(0)

def front_rightf(speed):
    GPIO.output(IN3, GPIO.HIGH); GPIO.output(IN4, GPIO.LOW)
    pwm_b1.ChangeDutyCycle(speed)

def front_rightb(speed):
    GPIO.output(IN3, GPIO.LOW); GPIO.output(IN4, GPIO.HIGH)
    pwm_b1.ChangeDutyCycle(speed)

def front_rights():
    GPIO.output(IN3, GPIO.LOW); GPIO.output(IN4, GPIO.LOW)
    pwm_b1.ChangeDutyCycle(0)

def back_rightf(speed):
    GPIO.output(IN5, GPIO.HIGH); GPIO.output(IN6, GPIO.LOW)
    pwm_a2.ChangeDutyCycle(speed)

def back_rightb(speed):
    GPIO.output(IN5, GPIO.LOW); GPIO.output(IN6, GPIO.HIGH)
    pwm_a2.ChangeDutyCycle(speed)

def back_rights():
    GPIO.output(IN5, GPIO.LOW); GPIO.output(IN6, GPIO.LOW)
    pwm_a2.ChangeDutyCycle(0)

def back_leftf(speed):
    GPIO.output(IN7, GPIO.HIGH); GPIO.output(IN8, GPIO.LOW)
    pwm_b2.ChangeDutyCycle(speed)

def back_leftb(speed):
    GPIO.output(IN7, GPIO.LOW); GPIO.output(IN8, GPIO.HIGH)
    pwm_b2.ChangeDutyCycle(speed)

def back_lefts():
    GPIO.output(IN7, GPIO.LOW); GPIO.output(IN8, GPIO.LOW)
    pwm_b2.ChangeDutyCycle(0)

def stop_all():
    front_lefts(); front_rights(); back_rights(); back_lefts()

def forward():
    front_leftf(SPEED); front_rightf(SPEED)
    back_leftf(SPEED);  back_rightf(SPEED)

def backward():
    front_leftb(SPEED); front_rightb(SPEED)
    back_leftb(SPEED);  back_rightb(SPEED)

def turn_left():
    front_leftb(SPEED); front_rightf(SPEED)
    back_leftb(SPEED);  back_rightf(SPEED)

def turn_right():
    front_leftf(SPEED); front_rightb(SPEED)
    back_leftf(SPEED);  back_rightb(SPEED)

# ultrasonic thread 

def distance_loop():
    global distance
    while running:
        GPIO.output(TRIG, False)
        time.sleep(0.00001)
        GPIO.output(TRIG, True)
        time.sleep(0.00001)
        GPIO.output(TRIG, False)
        timeout = time.time() + 0.05
        while GPIO.input(ECHO) == 0:
            if time.time() > timeout:
                break
        pulse_start = time.time()
        timeout = time.time() + 0.05
        while GPIO.input(ECHO) == 1:
            if time.time() > timeout:
                break
        pulse_end = time.time()
        d = ((pulse_end - pulse_start) * 34320) / 2
        with distance_lock:
            distance = round(d, 2)
        time.sleep(0.05)

sensor_thread = threading.Thread(target=distance_loop, daemon=True)
sensor_thread.start()

# servo motor thread
def servo_loop():
    global servo_pos, servo_dir
    while running:
        servo_pos += servo_dir * STEP
        if servo_pos >= MAX_ANGLE:
            servo_pos = MAX_ANGLE
            servo_dir = -1
        elif servo_pos <= MIN_ANGLE:
            servo_pos = MIN_ANGLE
            servo_dir = 1
        duty = 2 + (servo_pos / 18.0)
        servo_pwm.ChangeDutyCycle(duty)
        time.sleep(SERVO_INTERVAL)

servo_thread = threading.Thread(target=servo_loop, daemon=True)
servo_thread.start()

# lcd

I2C_ADDR      = 0x27
bus           = smbus2.SMBus(1)
LCD_CHR       = 1
LCD_CMD       = 0
LCD_LINE_1    = 0x80
LCD_LINE_2    = 0xC0
LCD_BACKLIGHT = 0x08
ENABLE        = 0b00000100

def lcd_byte(bits, mode):
    bits_high = mode | (bits & 0xF0) | LCD_BACKLIGHT
    bits_low  = mode | ((bits << 4) & 0xF0) | LCD_BACKLIGHT
    bus.write_byte(I2C_ADDR, bits_high)
    lcd_toggle_enable(bits_high)
    bus.write_byte(I2C_ADDR, bits_low)
    lcd_toggle_enable(bits_low)

def lcd_toggle_enable(bits):
    time.sleep(0.0005)
    bus.write_byte(I2C_ADDR, (bits | ENABLE))
    time.sleep(0.0005)
    bus.write_byte(I2C_ADDR, (bits & ~ENABLE))
    time.sleep(0.0005)

def lcd_init():
    lcd_byte(0x33, LCD_CMD)
    lcd_byte(0x32, LCD_CMD)
    lcd_byte(0x06, LCD_CMD)
    lcd_byte(0x0C, LCD_CMD)
    lcd_byte(0x28, LCD_CMD)
    lcd_byte(0x01, LCD_CMD)
    time.sleep(0.005)

def lcd_clear():
    lcd_byte(0x01, LCD_CMD)
    time.sleep(0.005)

def lcd_print(text, line):
    text = text.ljust(16)[:16]
    lcd_byte(line, LCD_CMD)
    for char in text:
        lcd_byte(ord(char), LCD_CHR)

lcd_init()
lcd_print("System Ready", LCD_LINE_1)
time.sleep(1)

# terrain mapper/visualizer

pygame.init()
WIDTH, HEIGHT = 800, 400
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Robot Radar")
clock = pygame.time.Clock()

MULTIPLIER   = 7.0
MAX_DISTANCE = 41.0
GREEN        = (0, 255, 0)
RED          = (255, 0, 0)
ORANGE       = (255, 165, 0)
DKGREEN      = (0, 40, 0)
BLACK        = (0, 0, 0)

trail        = []
MAX_TRAIL    = 150
font         = pygame.font.SysFont("monospace", 18)

fade_surface = pygame.Surface((WIDTH, HEIGHT))
fade_surface.set_alpha(18)
fade_surface.fill(BLACK)

lcd_counter  = 0

# keyboard inputs

def keyboard_loop():
    global running
    print("Drive Controller")
    print("────────────────")
    print("W : forward")
    print("S : backward")
    print("A : turn left")
    print("D : turn right")
    print("any other key : stop")
    print(f"Auto-stops within {SAFE_DISTANCE}cm")
    print("Q : quit")
    print("────────────────")

    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        while running:
            key = sys.stdin.read(1).lower()
            with distance_lock:
                d = distance

            if key == 'w':
                if 0 < d < SAFE_DISTANCE:
                    stop_all()
                else:
                    forward()
            elif key == 's':
                backward()
            elif key == 'a':
                turn_left()
            elif key == 'd':
                turn_right()
            elif key == 'q' or key == '\x03':
                running = False
            else:
                stop_all()
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)

kb_thread = threading.Thread(target=keyboard_loop, daemon=True)
kb_thread.start()

# auto braking

def safety_loop():
    while running:
        with distance_lock:
            d = distance
        if 0 < d < SAFE_DISTANCE:
            stop_all()
        time.sleep(0.05)

safety_thread = threading.Thread(target=safety_loop, daemon=True)
safety_thread.start()

# radar loop

try:
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

        with distance_lock:
            d = distance
        if d <= 0 or d > MAX_DISTANCE:
            d = MAX_DISTANCE

        angle_rad = (servo_pos / MAX_ANGLE) * math.pi
        trail.append((angle_rad, d))
        if len(trail) > MAX_TRAIL:
            trail.pop(0)

        lcd_counter += 1
        if lcd_counter >= 10:
            lcd_counter = 0
            lcd_print(f"Dist: {d:.1f}cm   ", LCD_LINE_1)
            lcd_print("TOO CLOSE!      " if d < SAFE_DISTANCE else "                ", LCD_LINE_2)

        screen.blit(fade_surface, (0, 0))
        cx = WIDTH // 2
        cy = HEIGHT

        for r in [10, 20, 30, 40]:
            pygame.draw.circle(screen, DKGREEN, (cx, cy), int(r * MULTIPLIER), 1)

        pygame.draw.circle(screen, ORANGE, (cx, cy), int(SAFE_DISTANCE * MULTIPLIER), 1)

        for i, (a, dist) in enumerate(trail):
            alpha = int(255 * (i / MAX_TRAIL))
            ex = cx - int(math.cos(a) * dist * MULTIPLIER)
            ey = cy - int(math.sin(a) * dist * MULTIPLIER)
            pygame.draw.line(screen, (0, alpha, 0), (cx, cy), (ex, ey), 1)

        ex = cx - int(math.cos(angle_rad) * d * MULTIPLIER)
        ey = cy - int(math.sin(angle_rad) * d * MULTIPLIER)
        beam_color = RED if d < SAFE_DISTANCE else GREEN
        pygame.draw.line(screen, beam_color, (cx, cy), (ex, ey), 3)

        max_ex = cx - int(math.cos(angle_rad) * MAX_DISTANCE * MULTIPLIER)
        max_ey = cy - int(math.sin(angle_rad) * MAX_DISTANCE * MULTIPLIER)
        pygame.draw.line(screen, RED, (ex, ey), (max_ex, max_ey), 3)

        screen.blit(font.render(f"Dist: {d:.1f}cm {'!! TOO CLOSE !!' if d < SAFE_DISTANCE else ''}", True, RED if d < SAFE_DISTANCE else GREEN), (10, 10))
        screen.blit(font.render("WASD to drive | ESC to quit", True, (80, 80, 80)), (10, 35))

        pygame.display.flip()
        clock.tick(60)

except KeyboardInterrupt:
    pass

finally:
    running = False
    stop_all()
    lcd_clear()
    servo_pwm.ChangeDutyCycle(0)
    servo_pwm.stop()
    for pwm in [pwm_a1, pwm_b1, pwm_a2, pwm_b2]:
        pwm.stop()
    GPIO.cleanup()
    pygame.quit()
    print("\nDone")
