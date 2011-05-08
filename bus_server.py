import time
import sys

import stomp

example_data = """[["one", "/queue/test.one"],
                ["two", "/queue/test.two"],
                ["three", "/queue/test.three"],
                ["colors",[["red", "/queue/test.red"],
                           ["blue", "/queue/test.blue"]]]]"""

def update_menu(menu_data):
    conn.send(example_data, destination='/topic/test.menu.changed')

class MyListener(object):
    def on_error(self, headers, message):
        print 'received an error %s' % message

    def on_message(self, headers, message):
        print 'received a message %s' % message
        conn.send(example_data, destination='/topic/test.menu')
        print 'sent off menu'

conn = stomp.Connection()
conn.set_listener('', MyListener())
conn.start()
conn.connect()

conn.subscribe(destination='/queue/test.request.menu', ack='auto')



try:
    while True:
        time.sleep(2)
except:
    conn.disconnect()

# idsb example:
# prod = cc.createProducerTemplate()
# cons = cc.createConsumerTemplate()
# cons.receiveBody("mq:test.two")
# prod.sendBody("mq:topic:test.notifications", "foo, bar, baz")
