import RPi.GPIO as GPIO
import time

ENA1 = 26
IN1 = 6
IN2 = 25
ENB1 = 19
IN3 = 16
IN4 = 20

ENA2 = 12
IN5 = 17
IN6 = 27
ENB2 = 13
IN7 = 22
IN8 = 5

GPIO.setmode(GPIO.BCM)

for pin in [
    ENA1, IN1, IN2,
    ENB1, IN3, IN4,
    ENA2, IN5, IN6,
    ENB2, IN7, IN8
]:
    GPIO.setup(pin, GPIO.OUT)

pwm_a1 = GPIO.PWM(ENA1, 1000)
pwm_b1 = GPIO.PWM(ENB1, 1000)
pwm_a2 = GPIO.PWM(ENA2, 1000)
pwm_b2 = GPIO.PWM(ENB2, 1000)

pwm_a1.start(0)
pwm_b1.start(0)
pwm_a2.start(0)
pwm_b2.start(0)

# m1, m2: motor drivers, each with motors a and b

def m1a_forward(speed=100):
    GPIO.output(IN1, GPIO.HIGH)
    GPIO.output(IN2, GPIO.LOW)
    pwm_a1.ChangeDutyCycle(speed)


def m1a_backward(speed=100):
    GPIO.output(IN1, GPIO.LOW)
    GPIO.output(IN2, GPIO.HIGH)
    pwm_a1.ChangeDutyCycle(speed)


def m1a_stop():
    GPIO.output(IN1, GPIO.LOW)
    GPIO.output(IN2, GPIO.LOW)
    pwm_a1.ChangeDutyCycle(0)


def m1b_forward(speed=100):
    GPIO.output(IN3, GPIO.HIGH)
    GPIO.output(IN4, GPIO.LOW)
    pwm_b1.ChangeDutyCycle(speed)


def m1b_backward(speed=100):
    GPIO.output(IN3, GPIO.LOW)
    GPIO.output(IN4, GPIO.HIGH)
    pwm_b1.ChangeDutyCycle(speed)


def m1b_stop():
    GPIO.output(IN3, GPIO.LOW)
    GPIO.output(IN4, GPIO.LOW)
    pwm_b1.ChangeDutyCycle(0)


def m2a_forward(speed=100):
    GPIO.output(IN5, GPIO.HIGH)
    GPIO.output(IN6, GPIO.LOW)
    pwm_a2.ChangeDutyCycle(speed)


def m2a_backward(speed=100):
    GPIO.output(IN5, GPIO.LOW)
    GPIO.output(IN6, GPIO.HIGH)
    pwm_a2.ChangeDutyCycle(speed)


def m2a_stop():
    GPIO.output(IN5, GPIO.LOW)
    GPIO.output(IN6, GPIO.LOW)
    pwm_a2.ChangeDutyCycle(0)


def m2b_forward(speed=100):
    GPIO.output(IN7, GPIO.HIGH)
    GPIO.output(IN8, GPIO.LOW)
    pwm_b2.ChangeDutyCycle(speed)


def m2b_backward(speed=100):
    GPIO.output(IN7, GPIO.LOW)
    GPIO.output(IN8, GPIO.HIGH)
    pwm_b2.ChangeDutyCycle(speed)


def m2b_stop():
    GPIO.output(IN7, GPIO.LOW)
    GPIO.output(IN8, GPIO.LOW)
    pwm_b2.ChangeDutyCycle(0)


def stop_all():
    m1a_stop()
    m1b_stop()
    m2a_stop()
    m2b_stop()


try:
    print("Module 1 Motor A forward")
    m1a_forward(75)
    time.sleep(2)

    m1a_stop()
    time.sleep(0.5)

except KeyboardInterrupt:
    stop_all()

finally:
    pwm_a1.stop()
    pwm_b1.stop()
    pwm_a2.stop()
    pwm_b2.stop()
    GPIO.cleanup()
    print("Done")
