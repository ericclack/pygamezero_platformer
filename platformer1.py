import random
import math

TEST_MODE = True

WORLD_SIZE = 20
BLOCK_SIZE = 32
WIDTH = WORLD_SIZE*BLOCK_SIZE
HEIGHT = WORLD_SIZE*BLOCK_SIZE

SPEED = 2
JUMP_SPEED = 4
GHOST_SPEED = 1
POWER_UP_START = 25

# An array containing the world tiles
world = []

# Our sprites
pacman = Actor('pacman_o.png')
pacman.x = pacman.y = 1.5*BLOCK_SIZE
# Direction that we're going in
pacman.dx, pacman.dy = 0,0
pacman.moving_x = pacman.moving_y = 0
# Other game variables
pacman.food_left = None
pacman.level = 1
pacman.powerup = 0
pacman.score = 0
pacman.lives = 3

# An array of ghosts
ghosts = []
# Where do the ghosts start?
ghost_start_pos = []

# Banner to display?
pacman.banner = None
pacman.banner_counter = 0

def set_banner(message, count):
    pacman.banner = message
    pacman.banner_counter = count

# Your level will contain characters, they map
# to the following images
char_to_image = {
    '.': 'dot.png',
    '=': 'wall.png',
    '*': 'power.png',
    'g': 'ghost1.png',
    'G': 'ghost3.png',
    'h': 'ghost4.png',
    'H': 'ghost5.png',
    '|': 'ladder.png',
}

def load_level(number):
    file = "level-%s.txt" % number
    pacman.food_left = 0

    with open(file) as f:
        for line in f:
            row = []
            for block in line.strip():
                row.append(block)
                if block == '.': pacman.food_left += 1
            world.append(row)

def new_ghost_direction(g):
    if pacman.powerup:
        g.dx = math.copysign(GHOST_SPEED*1.5, g.x - pacman.x)
        g.dy = math.copysign(GHOST_SPEED*1.5, g.y - pacman.y)
    else:
        g.dx = random.choice([-GHOST_SPEED, GHOST_SPEED])
        g.dy = random.choice([-GHOST_SPEED, GHOST_SPEED])
    g.moving_x = g.moving_y = 0

def make_ghost_actors():
    for y, row in enumerate(world):
        for x, block in enumerate(row):
            if block in ['g', 'G', 'h', 'H']:
                # Make the sprite in the correct position
                g = Actor(char_to_image[block], (x*BLOCK_SIZE, y*BLOCK_SIZE), anchor=('left', 'top'))
                g.orig_image = g.image
                new_ghost_direction(g)

                ghosts.append(g)
                ghost_start_pos.append((x,y))
                # Now we have the ghost sprite we don't need this block
                world[y][x] = None

def draw():
    screen.clear()
    for y, row in enumerate(world):
        for x, block in enumerate(row):
            image = char_to_image.get(block, None)
            if image:
                screen.blit(char_to_image[block], (x*BLOCK_SIZE, y*BLOCK_SIZE))
    pacman.draw()
    for g in ghosts: g.draw()
    screen.draw.text("Score: %s" % pacman.score, topleft=(8, 4), fontsize=40)
    screen.draw.text("Lives: %s" % pacman.lives, topright=(WIDTH-8,4), fontsize=40)

    if pacman.banner and pacman.banner_counter > 0:
        screen.draw.text(pacman.banner, center=(WIDTH/2, HEIGHT/2), fontsize=120)

def blocks_ahead_of(sprite, dx, dy):
    """Return a list of tiles at this position + delta"""

    # Here's where we want to move to, bit of rounding to
    # ensure we get the exact pixel position
    x = int(round(sprite.left)) + dx
    y = int(round(sprite.top)) + dy

    # Find integer block pos, using floor (so 4.7 becomes 4)
    ix,iy = int(x // BLOCK_SIZE), int(y // BLOCK_SIZE)
    # Remainder lets us check adjacent blocks
    rx, ry = x % BLOCK_SIZE, y % BLOCK_SIZE
    # Keep in bounds of world
    if ix == WORLD_SIZE-1: rx = 0
    if iy == WORLD_SIZE-1: ry = 0

    blocks = [ world[iy][ix] ]
    if rx: blocks.append(world[iy][ix+1])
    if ry: blocks.append(world[iy+1][ix])
    if rx and ry: blocks.append(world[iy+1][ix+1])

    if sprite==pacman: print((rx, ry))

    return blocks

def wrap_around(mini, val, maxi):
    if val < mini: return maxi
    elif val > maxi: return mini
    else: return val

def move_as_far_as_we_can(sprite, dx, dy):
    """Kove by dx,dy and if blocked move as far as we can."""

    # This only works for small-ish movements
    assert( abs(dx) < BLOCK_SIZE and abs(dy) < BLOCK_SIZE )

    # Can we move in direction dx, dy?
    if '=' not in blocks_ahead_of(sprite, dx, dy):
        sprite.x += dx
        sprite.y += dy
    else:
        # There's a block in the way!
        # Move as far as the edge of the block

        def pixels_to_edge_of_block(current_pos, direction):
            r = int(round(current_pos)) % BLOCK_SIZE
            if r == 0: return 0
            elif direction > 0: return BLOCK_SIZE - r
            else: return -r

        if dx: sprite.x += pixels_to_edge_of_block(sprite.left, dx)
        if dy: sprite.y += pixels_to_edge_of_block(sprite.top, dy)

        # Bounce off a ceiling for more realistic jumping
        if sprite == pacman and sprite.moving_y and dy < 0:
            if dy: sprite.dy = -dy/3

def move_sprite(sprite):
    # Record current pos so we can see if the sprite moved
    oldx, oldy = sprite.x, sprite.y

    # By moving x, then y, we can more easily get through gaps
    move_as_far_as_we_can(sprite, sprite.dx, 0)
    move_as_far_as_we_can(sprite, 0, sprite.dy)

    # Keep sprite on the screen
    sprite.x = wrap_around(0, sprite.x, WIDTH-BLOCK_SIZE)
    sprite.y = wrap_around(0, sprite.y, HEIGHT-BLOCK_SIZE)

    # Did we move?
    sprite.moving_y = oldy != sprite.y
    sprite.moving_x = oldx != sprite.x
    moved = sprite.moving_x or sprite.moving_y

    # Costume change for pacman
    if moved and sprite == pacman:
        a = 0
        if oldx < sprite.x: a = 0
        elif oldy > sprite.y: a = 90
        elif oldx > sprite.x: a = 180
        elif oldy < sprite.y: a = 270
        sprite.angle = a
    return moved

def touching_block(sprite, block, remove_it=False):
    ix,iy = int(pacman.x / BLOCK_SIZE), int(pacman.y / BLOCK_SIZE)
    touching = world[iy][ix] == block
    if touching and remove_it: world[iy][ix] = None
    return touching

def standing_on_block(sprite, blocks):
    ix,iy = int(pacman.x / BLOCK_SIZE), int(pacman.y / BLOCK_SIZE)
    blocks_below = blocks_ahead_of(sprite, 0, 1)
    for b in blocks:
        if b in blocks_below:
            return True
    return False

def eat_food():
    if touching_block(pacman, '.', True):
        pacman.food_left -= 1
        pacman.score += 1
    elif touching_block(pacman, '*', True):
        pacman.powerup = POWER_UP_START
        set_banner("Power Up!", 5)
        for g in ghosts: new_ghost_direction(g)
        pacman.score += 5

def reset_sprites():
    pacman.x = pacman.y = 1.5 * BLOCK_SIZE
    # Move ghosts back to their start pos
    for g, (x, y) in zip(ghosts, ghost_start_pos):
        animate(g, pos=(x * BLOCK_SIZE, y * BLOCK_SIZE))

def next_level():
    global world, ghosts, ghost_start_pos

    world = []
    ghosts = []
    ghost_start_pos = []

    pacman.level += 1
    load_level(pacman.level)
    make_ghost_actors()

    reset_sprites()

def update():
    # Gravity, if we're not on a ladder
    if not touching_block(pacman, '|'):
        pacman.dy = min(SPEED, pacman.dy + 0.1)

    # Regular movement
    move_sprite(pacman)
    eat_food()
    if pacman.food_left == 0:
        next_level()

    for g in ghosts:
        if not move_sprite(g):
            new_ghost_direction(g)
        if g.colliderect(pacman):
            if pacman.powerup:
                # Kill a ghost
                pass
            else:
                # Lose a life
                pacman.lives -= 1
                if pacman.lives > 0:
                    set_banner("Ouch!", 5)
                else:
                    set_banner("Game Over", 25)
                reset_sprites()

def on_key_up(key):
    if key in (keys.LEFT, keys.RIGHT):
        pacman.dx = 0
    if key in (keys.UP, keys.DOWN):
        pacman.dy = 0

    if TEST_MODE:
        # Put special key commands here
        if key == keys.N:
            next_level()

def on_key_down(key):
    if key == keys.LEFT:
        pacman.dx = -SPEED
    if key == keys.RIGHT:
        pacman.dx = SPEED
    if key == keys.UP and standing_on_block(pacman, ['=', '|']):
        # Jump
        pacman.dy = -JUMP_SPEED
    if key == keys.DOWN:
        pacman.dy = SPEED

def alternate(value, option1, option2):
    if value == option1: return option2
    else: return option1

def periodic():
    if pacman.banner_counter > 0:
        pacman.banner_counter -= 1

    if pacman.powerup > 0:
        pacman.powerup -= 1

        if pacman.powerup > 10:
            # The blue version for fleeing ghosts
            for g in ghosts: g.image = 'ghost2.png'
        else:
            # Flash for the last few seconds
            for g in ghosts:
                g.image = alternate(g.image, 'ghost_white.png', 'ghost2.png')

        if pacman.powerup == 0:
            for g in ghosts: g.image = g.orig_image

# Game set up
load_level(1)
make_ghost_actors()
clock.schedule_interval(periodic, 0.2)