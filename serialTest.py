import create2api
import time

#Create a Create2 Bot

bot = create2api.Create2()

bot.start()
bot.safe()

bot.digit_led_ascii('?#&h')
time.sleep(5)




# print 'Start Driving'
# bot.drive_straight(10)

# time.sleep(5)

# print 'Stop Driving'
# bot.drive_straight(0)


bot.destroy()