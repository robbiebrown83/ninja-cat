'''
Ninja Cat, 0.1a

Revolutionary Software, Robbie Sidell III

This game developed from code posted to StackOverflow by "sloth".
https://stackoverflow.com/questions/14354171/add-scrolling-to-a-platformer-in-pygame/14357169#14357169
At the time SO licensed under Attribution ShareAlike (CC BY-SA, 3.0)
https://creativecommons.org/licenses/by-sa/3.0/us/
'''

import pygame, sys, random, shelve
import pygame.font
import level_pack_1

class Game:
    def __init__(self):
        """Initialize game window"""
        pygame.init()
        
        #Initialize Settings
        self.FPS = 50 #frames per second setting
        self.fpsClock = pygame.time.Clock()
        self.WIN_WIDTH = 640
        self.HALF_WIDTH = int(self.WIN_WIDTH * 0.50)
        self.WIN_HEIGHT = 800
        self.HALF_HEIGHT = int(self.WIN_HEIGHT * 0.50)
        self.DISPLAY = (self.WIN_HEIGHT, self.WIN_WIDTH)
        self.WHITE = (255,255,255)
        self.RESOLUTION = 32 #i.e. pixels per block
        self.next_level = False #flag to load next level
        self.pause = False #flag to Pause
        self.level_index = 0
        self.levels = []
        self.buttons = []
        
        #Create window (width, height), flags, color_depth
        self.WINDOW = pygame.display.set_mode(self.DISPLAY)
        pygame.display.set_caption('Ninja Blocks')     
        
        #Create buttons
        self.play_button = Button(self.WINDOW, self.WIN_WIDTH * 0.25, self.WIN_HEIGHT * .50, "Play")
        self.next_level_btn = Button(self.WINDOW, self.WIN_WIDTH * 0.25, self.WIN_HEIGHT * 0.50, "Next Level")
        self.quit_button = Button(self.WINDOW, self.WIN_WIDTH * 0.75, self.WIN_HEIGHT * .50, "Quit")
        self.buttons.append(self.play_button)
        self.buttons.append(self.next_level_btn)
        self.buttons.append(self.quit_button)

    def new_game(self):
        """Title screen"""
        self.waiting = True
        self.play_button.draw_button()
        self.quit_button.draw_button()
        pygame.display.update()
        while self.waiting:
            self.button_check(self.buttons)
        self.player = Player(0, 0)
        self.playerSpawnX, self.playerSpawnY = 0,0
        self.begin_game()        
        
    def begin_game(self):
        """Start a new game"""
        #Initialize various groups, dictionaries
        #print("Begin Game")
        self.sprites = pygame.sprite.Group()
        self.sprites.add(self.player, self.player.sword)
        self.platforms = []
        self.walls = []
        self.enemies = []

        self.x = 0
        self.y = 0

        #initialize player references
        self.up = False
        self.down = False
        self.left = False
        self.right = False
        self.facing = "right"
        self.attack = False

        self.load_level()
        
        #initialize camera
        self.total_level_width = len(self.level[0]) * self.RESOLUTION
        self.total_level_height = len(self.level) * self.RESOLUTION
        self.camera = Camera(complex_camera, self.total_level_width, self.total_level_height)
        
        #initialize scoreboard
        self.score = Scoreboard(self.WINDOW, self.player)
        
        self.playing = True
        self.run_game()
        
    def load_level(self):
        """Preps and loads the current level"""
                
        #Open new level data via shelve.
        '''self.shelfFile = shelve.open('level_data')
        self.level = self.shelfFile['level']
        self.shelfFile.close()'''
        
        #Pre-fabbed level
        self.levels.append(level_pack_1.level0)
        self.levels.append(level_pack_1.level1)
        self.levels.append(level_pack_1.level2)
        
        self.level = self.levels[self.level_index]
        self.level_index = self.level_index + 1
        
        #build level
        for row in self.level:
            for col in row:
                if col == "S":
                    s = PlayerSpawn(self.x, self.y)
                    self.sprites.add(s)
                    self.platforms.append(s)
                    self.playerSpawnX, self.playerSpawnY = self.x, self.y
                if col == "P":
                    p = Platform(self.x,self.y)
                    self.platforms.append(p)
                    self.sprites.add(p)
                if col == "C":
                    c = Platform(self.x,self.y)
                    self.platforms.append(c)
                    self.sprites.add(c)
                if col == "W":
                    w = Wall(self.x, self.y)
                    self.walls.append(w)
                    self.sprites.add(w)
                if col == "E":
                    e = Enemy(self.x, self.y)
                    self.enemies.append(e)
                    self.sprites.add(e)
                if col == "X":
                    x = ExitBlock(self.x,self.y)
                    self.platforms.append(x)
                    self.sprites.add(x)
                if col == "B":
                    b = Base(self.x,self.y)
                    self.platforms.append(b)
                    self.sprites.add(b)
                self.x = self.x + self.RESOLUTION
            self.y = self.y + self.RESOLUTION
            self.x = 0
    
    def run_game(self):
        """Main game loop"""
        self.player.spawn(self.playerSpawnX, self.playerSpawnY)
        #print("Run Game")
        while self.playing:
            self.fpsClock.tick(self.FPS)
            self.events()
            self.update()
            self.draw()
            while self.pause:
                self.events()
        self.end_game()

    def button_check(self, buttons):
        """Checks on status of buttons"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.playing = False
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                for button in buttons:
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    button_clicked = button.rect.collidepoint(mouse_x, mouse_y)
                    if button_clicked and button == self.play_button:
                        self.waiting = False
                    if button_clicked and button == self.quit_button:
                        pygame.quit()
                        sys.exit()
                    if button_clicked and button == self.next_level_btn and self.next_level:
                        self.next_level = False
                        self.waiting = False
    
    def update(self):
        """Update game state"""
        self.camera.update(self.player)
        self.player.update(self.up, self.down, self.left, self.right, self.platforms, self.walls, self.attack, self.facing, self.enemies)
        for self.e in self.enemies:
            self.e.update(self.player, self.enemies, self.platforms, self.walls)
        self.score.prep_score()
        self.score.prep_lives()
        
    def events(self):
        """Event handling for game"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.playing = False
                pygame.quit()
                sys.exit()
            self.attack = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_UP:
                self.up = True
            if event.type == pygame.KEYDOWN and event.key == pygame.K_DOWN:
                self.down = True
            if event.type == pygame.KEYDOWN and event.key == pygame.K_LEFT:
                self.left = True
                self.facing = "left"
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RIGHT:
                self.right = True
                self.facing = "right"
            if event.type == pygame.KEYUP and event.key == pygame.K_UP:
                self.up = False
            if event.type == pygame.KEYUP and event.key == pygame.K_DOWN:
                self.down = False
            if event.type == pygame.KEYUP and event.key == pygame.K_RIGHT:
                self.right = False
            if event.type == pygame.KEYUP and event.key == pygame.K_LEFT:
                self.left = False
            if event.type == pygame.KEYUP and event.key == pygame.K_SPACE:
                self.attack = True
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                self.attack = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                if self.pause == False:
                    self.pause = True
                    break
                if self.pause == True:
                    self.pause = False
                    break
                               
    def draw(self):
        """Drawing items to screen for game"""
        self.WINDOW.fill(self.WHITE)
        for s in self.sprites:
            self.WINDOW.blit(s.image, self.camera.apply(s))
        self.score.draw_score()
        pygame.display.update()
        
    def end_game(self):
        """Ending the game"""
        #print("End Game")
        self.waiting = True
        if self.next_level:
            self.next_level_btn.draw_button()
            self.quit_button.draw_button()
        elif not self.next_level:
            self.level_index = 0
            self.player.score = 0
            self.play_button.draw_button()
            self.quit_button.draw_button()
        pygame.display.update()
        while self.waiting:
            self.button_check(self.buttons)
        self.begin_game()

class Camera(object):
    def __init__(self, camera_func, width, height):
        self.camera_func = camera_func
        self.state = pygame.Rect(0, 0, width, height)

    def apply(self, target):
        return target.rect.move(self.state.topleft)

    def update(self, target):
        self.state = self.camera_func(self.state, target.rect)

def simple_camera(camera, target_rect):
    l, t, _, _ = target_rect
    _, _, w, h = camera
    return Rect(-l+HALF_WIDTH, -t+HALF_HEIGHT, w, h)

def complex_camera(camera, target_rect):
    l, t, _, _ = target_rect
    _, _, w, h = camera
    l, t, _, _ = -l + g.HALF_WIDTH, -t + g.HALF_HEIGHT, w, h

    l = min(0, l)                           # stop scrolling at the left edge
    l = max(-(camera.width - g.WIN_HEIGHT), l)   # stop scrolling at the right edge
    t = max(-(camera.height - g.WIN_WIDTH), t) # stop scrolling at the bottom
    t = min(0, t)                           # stop scrolling at the top
    return pygame.Rect(l, t, w, h)

class Entity(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        
class Weapon(Entity):
    def __init__(self, x, y):
        Entity.__init__(self)
        self.image = pygame.Surface((int(g.RESOLUTION*0.75), int(g.RESOLUTION*0.25)))
        self.image.fill(pygame.Color("#e6e6ff"))
        self.image.convert()
        self.rect = pygame.Rect(x,y,int(g.RESOLUTION*0.75),int(g.RESOLUTION*0.25))
        self.strength = 1
        self.image.set_alpha(0) #transparent
        
    def update(self, player, sword_x, sword_y):
        self.rect.centerx = player.rect.centerx + sword_x
        self.rect.centery = player.rect.centery + sword_y
        self.image.set_alpha(256)
        
    def hide(self):
        self.rect.centerx, self.rect.centery = 0,0
        self.image.set_alpha(0)

class Player(Entity):
    def __init__(self, x, y):
        super(Player, self).__init__()
        """Entity.__init__(self)"""
        self.xvel = 0
        self.yvel = 0
        self.onGround = False
        self.jumpDownCheck = False
        self.wallCling = False
        self.damageLeft = False
        self.damageRight = False
        self.sword = Weapon(0,0)
        self.sword_coolDown = 500
        self.swordAvailable = True
        self.swordLastAttack = pygame.time.get_ticks()
        self.image = pygame.Surface((g.RESOLUTION,g.RESOLUTION))
        self.image.fill(pygame.Color("#0000FF"))
        self.image.convert()
        self.rect = pygame.Rect(x, y, g.RESOLUTION, g.RESOLUTION)
        self.life = 3
        self.jump_speed = 10
        self.run_speed = 5
        self.gravity = 0.3
        self.score = 0

    def spawn(self, x, y):
        """Spawn player"""
        self.rect = pygame.Rect(x, y, g.RESOLUTION, g.RESOLUTION)
        self.life = 3
        self.onGround = False
        self.wallCling = False
        self.jumpDownCheck = False
    
    def checkAttack(self):
        """Check that player available to attack"""
        if self.swordAvailable == False:
            self.swordCheck = pygame.time.get_ticks()
            if self.swordCheck - self.swordLastAttack >= self.sword_coolDown:
                self.swordAvailable = True
    
    def attack(self, weapon, facing):
        """Method for player attack, call sword"""
        if weapon == self.sword and self.swordAvailable:
            if facing == "left":
                sword_x = -25
                sword_y = 3
            if facing == "right":
                sword_x = 25
                sword_y = 3
            self.sword.update(self, sword_x, sword_y)
            self.swordAvailable = False
            self.swordLastAttack = pygame.time.get_ticks()

    def update(self, up, down, left, right, platforms, walls, attack, facing, enemies):
        self.checkAttack()
        if attack:
            self.attack(self.sword, facing)
            if up or down or left or right:
                self.sword.hide()
        if not attack:
            self.sword.hide()
        if self.wallCling:
            self.yvel = 0
            self.xvel = 0
            if left:
                self.xvel = self.jump_speed * -1
                self.yvel = self.run_speed * -1
                self.wallCling = False
            if right:
                self.xvel = self.jump_speed
                self.yvel = self.run_speed * -1
                self.wallCling = False
            if down:
                self.wallCling = False
        if not self.wallCling:
            if up:
                if self.onGround: # only jump if on the ground
                    self.yvel -= self.jump_speed
            if down:
                self.yvel += self.gravity
                self.jumpDownCheck = True
            if not down:
                self.jumpDownCheck = False
            if left:
                self.xvel = self.run_speed * -1
            if right:
                self.xvel = self.run_speed
            if not self.onGround and not self.wallCling:
                # only accelerate with gravity if in the air
                self.yvel += self.gravity
                # max falling speed
                if self.yvel > 100: self.yvel = 100
            if self.onGround and self.jumpDownCheck:
                self.jumpDownCheck = False
            if not(left or right):
                self.xvel = 0
            if self.damageLeft:
                self.xvel = self.run_speed * -5
                self.yvel = self.jump_speed * -0.5
                self.life -= 1
                self.damageLeft = False
            if self.damageRight:
                self.xvel = self.run_speed * 5
                self.yvel = self.jump_speed * -0.5
                self.life -= 1
                self.damageRight = False
        # increment in x direction
        self.rect.left += self.xvel
        # do x-axis collisions
        self.collide(self.xvel, 0, platforms, walls, enemies)
        # increment in y direction
        self.rect.top += self.yvel
        # assuming we're in the air
        self.onGround = False
        # do y-axis collisions
        self.collide(0, self.yvel, platforms, walls, enemies)
        if self.life < 0: #Loss of Life Death
            g.playing = False
        if self.rect.bottom > (g.WIN_HEIGHT): #Fall Death
            g.playing = False

    def collide(self, xvel, yvel, platforms, walls, enemies):
        for p in platforms:
            if pygame.sprite.collide_rect(self, p):
                if isinstance(p, ExitBlock):
                    g.playing = False #Note this updates the game state class
                    g.next_level = True
                if isinstance(p, PlayerSpawn):
                    break
                if isinstance(p, Base):
                    self.wallCling = True
                    self.jumpDownCheck = False
                if xvel > 0:
                    if self.jumpDownCheck:
                        break
                    self.rect.right = p.rect.left
                    self.wallCling = True
                    self.xvel = 0
                if xvel < 0:
                    if self.jumpDownCheck:
                        break
                    self.rect.left = p.rect.right
                    self.wallCling = True
                    self.xvel = 0
                if yvel > 0:
                    if self.jumpDownCheck:
                        self.onGround = False
                    else:
                        self.rect.bottom = p.rect.top
                        self.onGround = True
                        self.yvel = 0
                if yvel < 0:
                    self.rect.top = p.rect.bottom

        self.checkWalls(xvel, yvel, walls)
        for e in enemies:
            if pygame.sprite.collide_rect(self,e): #jump backs
                if self.rect.centerx > e.rect.centerx: #to the right
                    self.damageRight = True
                if self.rect.centerx < e.rect.centerx: #to the left
                    self.damageLeft = True
    
    def checkWalls(self, xvel, yvel, walls):
        for w in walls:
            if pygame.sprite.collide_rect(self, w):
                if xvel > 0: #right
                    self.rect.right = w.rect.left
                    self.xvel = 0
                if xvel < 0: #left
                    self.rect.left = w.rect.right
                    self.xvel = 0
                if yvel > 0:
                    self.rect.bottom = w.rect.top
                    self.onGround = True
                    self.yvel = 0
                if yvel < 0:
                    self.rect.top = w.rect.bottom

class Platform(Entity):
    def __init__(self, x, y):
        Entity.__init__(self)
        self.image = pygame.Surface((g.RESOLUTION, g.RESOLUTION))
        self.image.convert()
        self.image.fill(pygame.Color("#c9cbcf"))
        self.rect = pygame.Rect(x, y, g.RESOLUTION, g.RESOLUTION)

    def update(self):
        pass

class Base(Entity):
    def __init__(self, x, y):
        Entity.__init__(self)
        self.image = pygame.Surface((g.RESOLUTION, g.RESOLUTION))
        self.image.convert()
        self.image.fill(pygame.Color("#c9cbcf"))
        self.rect = pygame.Rect(x,y,g.RESOLUTION,g.RESOLUTION)
        
    def update(self):
        pass
        
class Wall(Entity):
    def __init__(self, x, y):
        Entity.__init__(self)
        self.image = pygame.Surface((g.RESOLUTION,g.RESOLUTION))
        self.image.convert()
        self.image.fill(pygame.Color("#60646c"))
        self.rect = pygame.Rect(x, y, g.RESOLUTION, g.RESOLUTION)
        
    def update(self):
        pass
                
class ExitBlock(Platform):
    def __init__(self, x, y):
        Platform.__init__(self, x, y)
        self.image.fill(pygame.Color("#cc7033"))

class PlayerSpawn(Platform):
    def __init__(self, x, y):
        Platform.__init__(self, x, y)
        self.image.fill(pygame.Color("#057D9F"))
        
class Enemy(Entity):
    """Holds enemies within Ninja Cats"""
    def __init__(self, x, y):
        Entity.__init__(self)
        self.image = pygame.Surface((g.RESOLUTION, g.RESOLUTION))
        self.image.fill(pygame.Color("#ae0404"))
        self.image.convert()
        self.rect = pygame.Rect(x, y, g.RESOLUTION, g.RESOLUTION)
        self.rect_lineOfSight = pygame.Rect(x-200, y, 400, 1)
        self.life = 1
        self.run_speed = 3
        self.xvel = 0
        self.yvel = 0
        self.gravity = 0.3
        self.onGround = False
    
    def update(self, player, enemies, platforms, walls):
        """Update function for enemies"""
        if not self.onGround:
            # only accelerate with gravity if in the air
            self.yvel += self.gravity
            # max falling speed
            if self.yvel > 100: self.yvel = 100
        # increment in x direction
        self.rect.left += self.xvel
        self.collide(self.xvel, 0, platforms, walls, player)
        # increment in y direction
        self.rect.top += self.yvel
        self.onGround = False
        # do y-axis collisions
        self.looking(player)
        self.collide(0, self.yvel, platforms, walls, player)
        self.destroy(enemies, player)
    
    def looking(self, player):
        """Function to examine whether Enemy Sees Player and Reacts"""
        self.rect_lineOfSight = pygame.Rect(self.rect.centerx-200, self.rect.centery, 400, 1)
        if pygame.Rect.colliderect(self.rect_lineOfSight, player):
            if self.rect.centerx > player.rect.centerx:
                self.rect.centerx -= self.run_speed
            if self.rect.centerx < player.rect.centerx:
                self.rect.centerx += self.run_speed
                
    def collide(self, xvel, yvel, platforms, walls, player):
        """Function to handle collisions between enemies and player's sword"""
        if pygame.Rect.colliderect(self.rect, player.sword.rect):
            self.life -= player.sword.strength
        for p in platforms:
            if pygame.sprite.collide_rect(self, p):
                if xvel > 0:
                    self.rect.right = p.rect.left
                    self.xvel = 0
                if xvel < 0:
                    self.rect.left = p.rect.right
                    self.xvel = 0
                if yvel > 0:
                    self.rect.bottom = p.rect.top
                    self.onGround = True
                    self.yvel = 0
                if yvel < 0:
                    self.rect.top = p.rect.bottom
        for w in walls:
            if pygame.sprite.collide_rect(self, w):
                if xvel > 0:
                    self.rect.right = w.rect.left
                    self.xvel = 0
                if xvel < 0:
                    self.rect.left = w.rect.right
                    self.xvel = 0
                if yvel > 0:
                    self.rect.bottom = w.rect.top
                    self.onGround = True
                    self.yvel = 0
                if yvel < 0:
                    self.rect.top = w.rect.bottom
                    
    def destroy(self, enemies, player):
        """Function to handle enemy destruction"""
        for i, e in enumerate(enemies):
            if e.life < 0:
                del enemies[i]
                player.score += 100
                self.image.set_alpha(0)

class Button(): #note needs import pygame.font
    """Build Buttons, edited Python Crash Course, Eric Matthes"""
    def __init__(self, screen, xOffset, yOffset, msg):
        """Init button attributes"""
        self.screen = screen
        self.screen_rect = screen.get_rect()

        #Set dimensions and properties of button
        self.width, self.height = 200,50
        self.button_color = (0,255,0)
        self.text_color = (255,255,255)
        self.font = pygame.font.SysFont(None, 48)

        #Build the button's rect object and center
        self.rect = pygame.Rect(0,0,self.width, self.height)
        self.rect.left = self.screen_rect.left + xOffset
        self.rect.top = self.screen_rect.bottom - yOffset

        #Button message needs to be prepped once
        self.prep_msg(msg)

    def prep_msg(self, msg):
        """Turn msg into a rendered image and center text on button."""
        self.msg_image = self.font.render(msg, True, self.text_color,
                                          self.button_color)
        self.msg_image_rect = self.msg_image.get_rect()
        self.msg_image_rect.center = self.rect.center
        
    def draw_button(self):
        self.screen.fill(self.button_color, self.rect)
        self.screen.blit(self.msg_image, self.msg_image_rect)

class Scoreboard(): #note needs import pygame.font
    """Class to report scoring information"""
    def __init__(self, screen, player):
        """Initialize attributes"""
        self.screen = screen
        self.screen_rect = screen.get_rect()
        self.player = player
        
        #Font Settings
        self.text_color = (30,30,30)
        self.font  = pygame.font.SysFont(None, 48)
        self.WHITE = (255,255,255)
        
        #Prep initial score image
        self.prep_score()
        self.prep_lives()
    
    def prep_score(self):
        """Turn score into image"""
        score_str = str(self.player.score)
        self.score_image = self.font.render(score_str, True, self.text_color, self.WHITE)
        
        #Display score in top center of screen
        self.score_rect = self.score_image.get_rect()
        self.score_rect.right = self.screen_rect.right - 20
        self.score_rect.top = 20
    
    def prep_lives(self):
        """Show how many lives we have left."""
        self.lives = pygame.sprite.Group()
        for life_num in range(self.player.life):
            life = Player(0,0)
            life.rect.x = 10 + life_num * life.rect.width * 2
            life.rect.y = 10
            self.lives.add(life)
    
    def draw_score(self):
        """Draw to score to screen"""
        self.screen.blit(self.score_image, self.score_rect)
        self.lives.draw(self.screen)

g = Game()
g.new_game()