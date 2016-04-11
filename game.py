import pygame
import math
from random import random
import keys
from pubnub import Pubnub

class Vec2:
    def __init__(self, x = 0, y = 0):
        self.x, self.y = x, y

    def __add__(self, v):
        return Vec2(self.x + v.x, self.y + v.y)

    def __sub__(self, v):
        return Vec2(self.x - v.x, self.y - v.y)

    def __mul__(self, alpha):
        return Vec2(self.x * alpha, self.y * alpha)

    def __rmul__(self, alpha):
        return Vec2(self.x * alpha, self.y * alpha)

    def intpair(self):
        return (int(self.x), int(self.y))

    def len(self):
        return math.sqrt(self.x * self.x + self.y * self.y)

class Rect:
    def __init__(self, left, top, right, bottom):
        self.left, self.top, self.right, self.bottom =\
            left, top, right, bottom

class Frame:
    def __init__(self, pressed, dt):
        self.pressed = pressed
        self.dt = dt

class Canvas:
    def __init__(self, screen):
        self.screen = screen

    def clear(self):
        self.screen.fill((0, 0, 0))

    def circle(self, color, pos, radius):
        pygame.draw.circle(self.screen, color, pos, radius)

class Player:
    def refresh_color(self):
        """Set color (it depens on the module of Player speed)"""
        self.color = min(255, int(self.v.len()) + 100)

    def __init__(self, pos, rect, a = 500, radius = 20, uid = None, local = False):
        """Constructor of Player class
        self.a - acceleration coef.
        self.r - radius
        """
        self.uid = uid if uid else random()
        self.pos, self.a, self.r, self.local = Vec2(*pos), a, radius, local
        self.pressed = { pygame.K_RIGHT : 0, pygame.K_LEFT : 0,
                         pygame.K_DOWN : 0, pygame.K_UP : 0 }
        self.rect = rect
        self.v = Vec2()
        self.refresh_color()

    def handle_border(self):
        if self.pos.x - self.r < self.rect.left:
            if self.v.x < 0:
                self.v.x = -self.v.x
            self.pos.x = self.rect.left + self.r
        if self.pos.y - self.r < self.rect.top:
            if self.v.y < 0:
                self.v.y = -self.v.y


            self.pos.y = self.rect.top + self.r
        if self.pos.x + self.r > self.rect.right:
            if self.v.x > 0:
                self.v.x = -self.v.x
            self.pos.x = self.rect.right - self.r;
        if self.pos.y + self.r > self.rect.bottom:
            if self.v.y > 0:
                self.v.y = -self.v.y
            self.pos.y = self.rect.bottom - self.r

    def set_pressed(self, pressed):
        self.pressed[pygame.K_RIGHT] = pressed.get(pygame.K_RIGHT, 0)
        self.pressed[pygame.K_LEFT] = pressed.get(pygame.K_LEFT, 0)
        self.pressed[pygame.K_DOWN] = pressed.get(pygame.K_DOWN, 0)
        self.pressed[pygame.K_UP] = pressed.get(pygame.K_UP, 0)

    def set_pos(self, pos, v):
        self.pos = Vec2(*pos)
        self.v = Vec2(*v)

    def update(self, dt):
        """Update Player state"""
        f = Vec2()
        f.x = self.pressed[pygame.K_RIGHT] - self.pressed[pygame.K_LEFT];
        f.y = self.pressed[pygame.K_DOWN] - self.pressed[pygame.K_UP];
        f *= self.a
        self.v = self.v + dt * (f - self.v)
        self.pos += dt * self.v

        self.handle_border()

        self.refresh_color()

    def render(self, canvas):
        """Draw Player on the Game window"""
        canvas.circle((self.color, self.color, self.color),
                      self.pos.intpair(), self.r)

class Net:
    def callback(self, message):
        print(message)

    def __init__(self, channel = "my_channel_sf23"):
        self.channel = channel
        self.pubnub = Pubnub(publish_key=keys.PUB_KEY,
                subscribe_key=keys.SUB_KEY)

    def subscribe(self, callback):
        self.pubnub.subscribe(channels=self.channel,
                callback=callback, error=self.callback)

    def unsubscribe(self):
        self.pubnub.unsubscribe(channel=self.channel)

    def publish(self, message):
        self.pubnub.publish(channel=self.channel, message=message,
                callback=self.callback, error=self.callback)

class World:
    def __init__(self, rect):
        self.rect = rect
        self.units = []
        self.frame = Frame(pygame.key.get_pressed(), 0)

    def set_frame(self, frame):
        self.frame = frame

    def update(self):
        for u in self.units:
            if u.local:
                u.set_pressed(dict(enumerate(self.frame.pressed)))

            u.update(self.frame.dt)

    def find_unit_by_uid(self, uid):
        for u in self.units:
            if u.uid == uid:
                return u

        return None

    def render(self, canvas):
        canvas.clear()
        for u in self.units:
            u.render(canvas)

    def addUnit(self, u):
        self.units.append(u)

    def sync(self, message, channel):
        u = self.find_unit_by_uid(message["uid"])
        if (u):
            if u.local:
                return

            u.set_pos((message["x"], message["y"]),
                      (message["vx"], message["vy"]))
        else:
            u = Player((message["x"], message["y"]), rect = self.rect,
                       uid = message["uid"])
            self.addUnit(u)

        """Pubnub changes keys from int to string, revert it"""
        u.set_pressed({ int(i) : message["pressed"].get(i)
                       for i in message["pressed"].keys() })

    def send_sync(self, net):
        for u in self.units:
            if u.local:
                u.set_pressed(dict(enumerate(self.frame.pressed)))
                message = { "uid" : u.uid,
                            "x" : u.pos.x,
                            "y" : u.pos.y,
                            "vx" : u.v.x,
                            "vy" : u.v.y,
                            "pressed" : u.pressed }
                net.publish(message)

class Game:
    def __init__(self):
        self._running = True
        self.size = self.width, self.height = 640, 400
        self.screen = pygame.display.set_mode(self.size, pygame.HWSURFACE)
        pygame.display.set_caption('Game')
        self.clock = pygame.time.Clock()

        self.canvas = Canvas(self.screen)

        self.world = World(Rect(0, 0, self.width, self.height))
        self.world.addUnit(Player(pos = (50, 50), rect = self.world.rect, local = True))

        self.net = Net()
        self.net.subscribe(self.world.sync)

    def exit(self):
        """Exit the game"""
        self._running = False

    def handle_event(self, event):
        """Handling one pygame event"""
        if event.type == pygame.QUIT:
            # close window event
            self.exit()
        elif event.type == pygame.KEYDOWN:
            # keyboard event on press ESC
            if event.key == pygame.K_ESCAPE:
                self.exit()
        if event.type in (pygame.KEYDOWN, pygame.KEYUP) \
           and event.key in (pygame.K_RIGHT, pygame.K_LEFT,
                             pygame.K_DOWN, pygame.K_UP):
            """Update pressed for smooth sync"""
            self.world.set_frame(Frame(pygame.key.get_pressed(),
                   self.world.frame.dt))
            self.world.send_sync(self.net)


    def cleanup(self):
        """Cleanup the Game"""
        pygame.quit()
        self.net.unsubscribe()

    def execute(self):
        """Execution loop of the game"""
        while self._running:
            # get all pygame events from queue
            for event in pygame.event.get():
                self.handle_event(event)

            dt = self.clock.tick(50) / 1000.0
            self.world.set_frame(Frame(pygame.key.get_pressed(), dt))

            self.world.update()
            self.world.render(self.canvas)
            pygame.display.flip()

        self.cleanup()

if __name__ == "__main__":
    game = Game()
    game.execute()
