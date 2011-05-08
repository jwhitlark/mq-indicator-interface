import gobject
import gtk
import appindicator
import pynotify
import stomp
import os

gtk.gdk.threads_init()

# refactor out app name, use common set of channels
# test /topic/menu_change

# listener for other status changes

# additional fields after channel to set headers, body?

menu_set = False

class MyListener(object):
    def on_error(self, headers, message):
        print 'received an error %s' % message

    def on_message(self, headers, message):
        print 'received a message %s, with headers %s' % (message, headers)

        if headers['destination'] == '/topic/test.menu' and menu_set is False:
            menu_data = eval(message)
            update_main_menu(menu_data)

        elif headers['destination'] == '/topic/test.menu.changed':
            menu_data = eval(message)
            update_main_menu(menu_data)

        elif headers['destination'] == '/topic/test.notifications':
            notification = pynotify.Notification("bus indicator test app", message)
            notification.show()

        else:
            print "got a different message... %s, %s" % (headers, message)


def update_main_menu(menu_data):
    global menu_set
    menu_set = True

    conn.subscribe(destination='/topic/test.menu.changed', ack='auto')
    menu = gtk.Menu()
    add_to_menu(menu, menu_data)
    ind.set_menu(menu)
    add_indicator_quit(menu)


ind = appindicator.Indicator ("bus panel test",
                              "mq-panel",
                              appindicator.CATEGORY_APPLICATION_STATUS)


conn = stomp.Connection()
conn.set_listener('', MyListener())
conn.start()
conn.connect()

conn.subscribe(destination='/topic/test.menu', ack='auto')
conn.subscribe(destination='/topic/test.notifications', ack='auto')

# example_data = [["one", "/queue/test.one"],
#                 ["two", "/queue/test.two"],
#                 ["three", "/queue/test.three"],
#                 ["colors",[["red", "/queue/test.red"],
#                            ["blue", "/queue/test.blue"]]]]


def create_func(channel):
    def send_msg(w, buf):
        print "sending %s, to %s" % (buf, channel)
        conn.send(buf, destination=channel)
    return send_msg

def add_item(menu, name, channel):
    item = gtk.MenuItem(name)
    item.show()
    menu.append(item)
    func = create_func(channel)
    item.connect("activate", func, 'hello to %s from bus indicator' % channel)


def add_to_menu(menu, data):
    for x in data:
        if isinstance(x[1], basestring):
            print "adding item %s with channel %s" % (x[0], x[1])
            add_item(menu, x[0], x[1])
        else:
            print "adding %s as menu" % x[0]
            print "passed data is %s" % x[1]
            submenu = gtk.Menu()
            submenu_item = gtk.MenuItem(x[0])
            submenu_item.set_submenu(submenu)
            submenu_item.show()
            menu.append(submenu_item)
            add_to_menu(submenu, x[1])

def quit(w):
    print "asked to quit"
    conn.disconnect()
    gtk.main_quit()

def add_indicator_quit(menu):
    item = gtk.MenuItem("quit indicator")
    item.show()
    menu.append(item)
    item.connect("activate", quit)

if __name__ == "__main__":

    ind.set_icon_theme_path(os.getcwd())
    ind.set_status (appindicator.STATUS_ACTIVE)
    ind.set_attention_icon ("indicator-messages-new")

    # send initial message
    conn.send('', destination='/queue/test.request.menu')

    gtk.main()
