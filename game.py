import pygame
import math

class Player:
    def refresh_color(self):
        """Set color(it depens on the module of Player speed)"""
        self.color = min(255, int(math.sqrt(self.vx ** 2
            + self.vy ** 2)) + 100)

    def __init__(self, x = 100, y = 100, vx = 0, vy = 0, a = 500, r = 20):
        """Constructor of Player class"""
        """self.a - acceleration"""
        """self.r - radius"""
        self.x, self.y, self.vx, self.vy, self.a, self.r = \
                x, y, vx, vy, a, r
        self.refresh_color()

    def update(self, game):
        """Update Player state"""
        if game.pressed[pygame.K_LEFT]:
            self.vx -= game.delta * self.a
        if game.pressed[pygame.K_RIGHT]:
            self.vx += game.delta * self.a
        if game.pressed[pygame.K_UP]:
            self.vy -= game.delta * self.a
        if game.pressed[pygame.K_DOWN]:
            self.vy += game.delta * self.a

        self.vx -= game.delta * self.vx
        self.vy -= game.delta * self.vy

        self.x += self.vx * game.delta
        self.y += self.vy * game.delta

        """Do not let Player get out of the Game window"""
        if self.x < self.r:
            if self.vx < 0:
                self.vx = -self.vx
            self.x = self.r
        if self.y < self.r:
            if self.vy < 0:
                self.vy = -self.vy
            self.y = self.r
        if self.x > game.width - self.r:
            if self.vx > 0:
                self.vx = -self.vx
            self.x = game.width - self.r
        if self.y > game.height - self.r:
            if self.vy > 0:
                self.vy = -self.vy
            self.y = game.height - self.r

        self.refresh_color()

    def render(self, game):
        """Draw Player on the Game window"""
        pygame.draw.circle(game.screen,
                (self.color, self.color, self.color),
                (int(self.x), int(self.y)), self.r)

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
        self.player = Player()
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
        self.ar[int(self.player.x/10.0),int(self.player.y/10.0)] = (200,200,200)
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
