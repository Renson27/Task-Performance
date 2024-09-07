import pygame
import random

pygame.init()

# Screen and grid settings
SCREEN_WIDTH = 400  # Increased width for preview
SCREEN_HEIGHT = 600
BLOCK_SIZE = 30
GRID_WIDTH = 10
GRID_HEIGHT = SCREEN_HEIGHT // BLOCK_SIZE
PREVIEW_WIDTH = 4  # Width of the preview area
PREVIEW_HEIGHT = 4  # Height of the preview area
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)

SHAPES = [
    [[1, 1, 1, 1]],  # I
    [[1, 1], [1, 1]],  # O
    [[0, 1, 1], [1, 1, 0]],  # S
    [[1, 1, 0], [0, 1, 1]],  # Z
    [[1, 1, 1], [0, 1, 0]],  # T
    [[1, 1, 1], [1, 0, 0]],  # L
    [[1, 1, 1], [0, 0, 1]]   # J
]

SHAPE_COLORS = [CYAN, YELLOW, GREEN, RED, BLUE, ORANGE, MAGENTA]

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Tetris')
font = pygame.font.SysFont(None, 36)

def draw_block(x, y, color):
    pygame.draw.rect(screen, color, (x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE))
    pygame.draw.rect(screen, BLACK, (x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE), 1)

def draw_grid():
    for x in range(GRID_WIDTH):
        for y in range(GRID_HEIGHT):
            draw_block(x, y, WHITE)

def draw_grid_blocks(grid):
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            if grid[y][x]:
                draw_block(x, y, grid[y][x])

def draw_text(text, color, position):
    text_surface = font.render(text, True, color)
    screen.blit(text_surface, position)

def draw_preview(shape, color):
    preview_x = GRID_WIDTH + 1  # Adjusted for preview space
    preview_y = 2
    for y, row in enumerate(shape):
        for x, cell in enumerate(row):
            if cell:
                draw_block(preview_x + x, preview_y + y, color)

def check_collision(grid, shape, offset):
    shape_x, shape_y = offset
    for y, row in enumerate(shape):
        for x, cell in enumerate(row):
            if cell:
                if (shape_x + x < 0 or shape_x + x >= GRID_WIDTH or
                    shape_y + y >= GRID_HEIGHT or grid[shape_y + y][shape_x + x]):
                    return True
    return False

def merge_shape(grid, shape, offset):
    shape_x, shape_y = offset
    for y, row in enumerate(shape):
        for x, cell in enumerate(row):
            if cell:
                grid[shape_y + y][shape_x + x] = shape[y][x]

def clear_rows(grid):
    full_rows = [i for i, row in enumerate(grid) if all(row)]
    for i in full_rows:
        del grid[i]
        grid.insert(0, [0] * GRID_WIDTH)
    return len(full_rows)

def rotate_shape(shape):
    return [list(row) for row in zip(*shape[::-1])]

def new_shape():
    shape = random.choice(SHAPES)
    color = SHAPE_COLORS[SHAPES.index(shape)]
    return shape, color

def drop_shape_fast(grid, shape, offset):
    shape_x, shape_y = offset
    while not check_collision(grid, shape, (shape_x, shape_y + 1)):
        shape_y += 1
    return shape_x, shape_y

def game_loop():
    grid = [[0] * GRID_WIDTH for _ in range(GRID_HEIGHT)]
    clock = pygame.time.Clock()
    current_shape, current_color = new_shape()
    preview_shape, preview_color = new_shape()
    shape_x, shape_y = GRID_WIDTH // 2, 0
    score = 0
    fall_speed = 500  # milliseconds
    game_over = False
    last_fall_time = pygame.time.get_ticks()
    space_pressed = False
    shift_pressed = False
    swapped = False

    while not game_over:
        screen.fill(BLACK)
        draw_grid()
        draw_grid_blocks(grid)
        for y, row in enumerate(current_shape):
            for x, cell in enumerate(row):
                if cell:
                    draw_block(shape_x + x, shape_y + y, current_color)
        draw_text(f'Score: {score}', WHITE, (10, 10))
        
        # Draw the preview shape
        draw_preview(preview_shape, preview_color)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    shape_x -= 1
                    if check_collision(grid, current_shape, (shape_x, shape_y)):
                        shape_x += 1
                elif event.key == pygame.K_RIGHT:
                    shape_x += 1
                    if check_collision(grid, current_shape, (shape_x, shape_y)):
                        shape_x -= 1
                elif event.key == pygame.K_DOWN:
                    shape_y += 1
                    if check_collision(grid, current_shape, (shape_x, shape_y)):
                        shape_y -= 1
                        merge_shape(grid, current_shape, (shape_x, shape_y))
                        score += clear_rows(grid)
                        current_shape, current_color = new_shape()
                        shape_x, shape_y = GRID_WIDTH // 2, 0
                        if check_collision(grid, current_shape, (shape_x, shape_y)):
                            game_over = True
                elif event.key == pygame.K_UP:
                    rotated_shape = rotate_shape(current_shape)
                    if not check_collision(grid, rotated_shape, (shape_x, shape_y)):
                        current_shape = rotated_shape
                elif event.key == pygame.K_SPACE:
                    if not space_pressed:
                        shape_x, shape_y = drop_shape_fast(grid, current_shape, (shape_x, shape_y))
                        merge_shape(grid, current_shape, (shape_x, shape_y))
                        score += clear_rows(grid)
                        current_shape, current_color = new_shape()
                        shape_x, shape_y = GRID_WIDTH // 2, 0
                        if check_collision(grid, current_shape, (shape_x, shape_y)):
                            game_over = True
                    space_pressed = True
                elif event.key == pygame.K_LSHIFT or event.key == pygame.K_RSHIFT:
                    if not shift_pressed:
                        if not swapped:
                            # Swap the current and preview shapes
                            current_shape, current_color = preview_shape, preview_color
                            preview_shape, preview_color = new_shape()
                            shape_x, shape_y = GRID_WIDTH // 2, 0
                            if check_collision(grid, current_shape, (shape_x, shape_y)):
                                game_over = True
                            swapped = True
                        else:
                            # Swap back to the original shape
                            preview_shape, preview_color = current_shape, current_color
                            current_shape, current_color = new_shape()
                            shape_x, shape_y = GRID_WIDTH // 2, 0
                            if check_collision(grid, current_shape, (shape_x, shape_y)):
                                game_over = True
                            swapped = False
                    shift_pressed = True
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_SPACE:
                    space_pressed = False
                elif event.key == pygame.K_LSHIFT or event.key == pygame.K_RSHIFT:
                    shift_pressed = False

        current_time = pygame.time.get_ticks()
        if current_time - last_fall_time > fall_speed:
            shape_y += 1
            if check_collision(grid, current_shape, (shape_x, shape_y)):
                shape_y -= 1
                merge_shape(grid, current_shape, (shape_x, shape_y))
                score += clear_rows(grid)
                current_shape, current_color = new_shape()
                shape_x, shape_y = GRID_WIDTH // 2, 0
                if check_collision(grid, current_shape, (shape_x, shape_y)):
                    game_over = True
            last_fall_time = current_time

        pygame.time.delay(10)  # Short delay to control CPU usage

if __name__ == "__main__":
    game_loop()
    pygame.quit()