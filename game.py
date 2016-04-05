import pygame
import math

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


class Player:
    def refresh_color(self):
        """Set color (it depens on the module of Player speed)"""
        self.color = min(255, int(self.v.len()) + 100)

    def __init__(self, pos, a = 500, r = 20):
        """Constructor of Player class
        self.a - acceleration coef.
        self.r - radius
        """
        self.pos, self.a, self.r = Vec2(*pos), a, r
        self.v = Vec2()
        self.refresh_color()

    def update(self, game):
        """Update Player state"""
        f = Vec2()
        f.x = game.pressed[pygame.K_RIGHT] - game.pressed[pygame.K_LEFT];
        f.y = game.pressed[pygame.K_DOWN] - game.pressed[pygame.K_UP];
        f *= self.a

        self.v = self.v + game.delta * (f - self.v)

        self.pos += game.delta * self.v

        """Do not let Player get out of the Game window"""
        if self.pos.x < self.r:
            if self.v.x < 0:
                self.v.x = -self.v.x
            self.pos.x = self.r
        if self.pos.y < self.r:
            if self.v.y < 0:
                self.v.y = -self.v.y
            self.pos.y = self.r
        if self.pos.x > game.width - self.r:
            if self.v.x > 0:
                self.v.x = -self.v.x
            self.pos.x = game.width - self.r
        if self.pos.y > game.height - self.r:
            if self.v.y > 0:
                self.v.y = -self.v.y
            self.pos.y = game.height - self.r

        self.refresh_color()

    def render(self, game):
        """Draw Player on the Game window"""
        pygame.draw.circle(game.screen,
                (self.color, self.color, self.color),
                self.pos.intpair(), self.r)

class Game:
    def tick(self):
        """Return time in seconds since previous call
        and limit speed of the game to 50 fps"""
        self.delta = self.clock.tick(50) / 1000.0

    def __init__(self):
        """Constructor of the Game"""
        self._running = True
        self.size = self.width, self.height = 640, 400
        # create main display - 640x400 window
        # try to use hardware acceleration
        self.screen = pygame.display.set_mode(self.size, pygame.HWSURFACE)
        # set window caption
        pygame.display.set_caption('Game')
        # get object to help track time
        self.clock = pygame.time.Clock()
        # set default tool
        self.tool = 'run'
        self.player = Player((50, 50))
        self.ar = pygame.PixelArray(self.screen)

    def event_handler(self, event):
        """Handling one pygame event"""
        if event.type == pygame.QUIT:
            # close window event
            self.exit()
        elif event.type == pygame.KEYDOWN:
            # keyboard event on press ESC
            if event.key == pygame.K_ESCAPE:
                self.exit()

    def move(self):
        """Here game objects update their positions"""
        self.tick()
        self.pressed = pygame.key.get_pressed()

        self.player.update(self)

    def render(self):
        """Render the scene"""
        self.screen.fill((0, 0, 0))
        self.player.render(self)
        self.ar[int(self.player.pos.x/10.0),int(self.player.pos.y/10.0)] = (200,200,200)
        pygame.display.flip()

    def exit(self):
        """Exit the game"""
        self._running = False

    def cleanup(self):
        """Cleanup the Game"""
        pygame.quit()

    def execute(self):
        """Execution loop of the game"""
        while(self._running):
            # get all pygame events from queue
            for event in pygame.event.get():
                self.event_handler(event)
            self.move()
            self.render()
        self.cleanup()

if __name__ == "__main__":
    game = Game()
    game.execute()
