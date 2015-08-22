import create2api
import time

#Create a Create2 Bot

bot = create2api.Create2()

bot.start()
bot.safe()

# bot.digit_led_ascii('DATE')
# time.sleep(1)
# bot.digit_led_ascii('TEST')

# time.sleep(1)

# bot.set_day_time('Friday', 17, 40)




print 'forwad'
bot.drive_straight(200)
#bot.drive(-200, 500)

time.sleep(1)
print 'back'
bot.drive_straight(-200)
#bot.drive(200, 500)
time.sleep(1)
print 'Stop Driving'
#bot.drive(0,0)
bot.drive_straight(0)
bot.reset()


bot.destroy()