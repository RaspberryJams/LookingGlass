from picamera import PiCamera, Color
import time
import RPi.GPIO as GPIO
from datetime import datetime
from datetime import timedelta

segCode = [0x3f,0x06,0x5b,0x4f,0x66,0x6d,0x7d,0x07,0x7f,0x6f,0x77,0x7c,0x39,0x5e,0x79,0x71,0x80]

camera = PiCamera()
BeepPin = 15
BtnPin = 16    # pin12 --- button

SDI   = 11
RCLK  = 12
SRCLK = 13


def setup():
    GPIO.setmode(GPIO.BOARD)       # Numbers GPIOs by physical location
    GPIO.setup(BtnPin, GPIO.IN, pull_up_down=GPIO.PUD_UP)    # Set BtnPin's mode is input, and pull up to high level(3.3V)
    GPIO.setup(BeepPin, GPIO.OUT)   # Set BeepPin's mode is output
    GPIO.output(BeepPin, GPIO.HIGH) # Set BeepPin high(+3.3V) to off beep
    GPIO.setup(SDI, GPIO.OUT)
    GPIO.setup(RCLK, GPIO.OUT)
    GPIO.setup(SRCLK, GPIO.OUT)
    GPIO.output(SDI, GPIO.LOW)
    GPIO.output(RCLK, GPIO.LOW)
    GPIO.output(SRCLK, GPIO.LOW)
    
def swPhoto(ev=None):
    global pressTime
    global timePicOne
    global numPics
    global betweenPics
    global namePhotoshoot
    global personNum
    if datetime.now() > ( pressTime + timedelta(seconds=3) ):
        #camera.start_preview()
        personNum = personNum + 1
        camera.annotate_text = "Look above for the\ncountdown to each picture"
        camera.annotate_text_size = 160
        #camera.annotate_foreground = Color('red')
        time.sleep(timePicOne)
        camera.annotate_text = ""
        for i in range(numPics):
            for p in range (betweenPics):
                pic = betweenPics - p
                #camera.annotate_text = "%s" % pic
                hc595_shift(segCode[pic])
                time.sleep(1) 
            
            hc595_shift(segCode[0])
            time.sleep(.5)
            GPIO.output(BeepPin, GPIO.LOW)
            time.sleep(0.5)
            GPIO.output(BeepPin, GPIO.HIGH)    # beep off
            time.sleep(0.1)
            camera.capture('/home/pi/Desktop/Projects/PhotoBooth/Images/%s-%s-%s.jpg' % (namePhotoshoot,personNum,i))
        #camera.stop_preview()
        #name = input('please enter your name: ')
        #print('hello, ', name)
        camera.annotate_text = 'Push button to begin\ntaking your photos.'
        pressTime = datetime.now()



def hc595_shift(dat):
	for bit in range(0, 8):	
		GPIO.output(SDI, 0x80 & (dat << bit))
		GPIO.output(SRCLK, GPIO.HIGH)
		time.sleep(0.001)
		GPIO.output(SRCLK, GPIO.LOW)
	GPIO.output(RCLK, GPIO.HIGH)
	time.sleep(0.001)
	GPIO.output(RCLK, GPIO.LOW)
	
def loop():
    GPIO.add_event_detect(BtnPin, GPIO.FALLING, callback=swPhoto) # wait for falling
    camera.start_preview()
    camera.rotation = 90
    camera.resolution = (1944, 2592) #, 1944)
    while True:
        pass   # Don't do anything

def destroy():
        camera.stop_preview()
        GPIO.cleanup()                     # Release resource

if __name__ == '__main__':     # Program start from here
    namePhotoshoot = input('please enter the name of the photoshoot: ')
    numPics = int(input('how many pictures do you want: '))
    timePicOne = int(input('how many seconds do you want to get ready for the first picture: '))
    if timePicOne > 9:
        timePicOne = 9
    betweenPics = int(input('how many seconds do you want in between all the other pictures: '))
    #number = int(numPics)
    personNum = 0
    #timeOne = int(timePicOne)
    #timeRest = int(betweenPics)
    print('the name of your photoshoot is ', namePhotoshoot,
          'you want ', numPics, 'pictures taken',
          'you want ', timePicOne, 'seconds to prepare for the first picture. ',
          'you want ',betweenPics, 'seconds between every other picture.')
    pressTime = datetime.now()
    setup()
    try:
        loop()
    except KeyboardInterrupt:  # When 'Ctrl+C' is pressed, the child program destroy() will be  executed.
        destroy()

