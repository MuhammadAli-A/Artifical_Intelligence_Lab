import pygame
import random
import heapq
import math
import sys

# ---------------- Maze Class ----------------
class Maze:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.grid = [[1 for _ in range(width)] for _ in range(height)]
        self.start = (1, 1)
        self.goal = (width-2, height-2)
        self.generate_maze()

    def generate_maze(self):
        stack = [self.start]
        self.grid[self.start[1]][self.start[0]] = 0
        directions = [(0, 2), (2, 0), (0, -2), (-2, 0)]
        while stack:
            x, y = stack[-1]
            neighbors = []
            for dx, dy in directions:
                nx, ny = x + dx, y + dy
                if 0 < nx < self.width-1 and 0 < ny < self.height-1 and self.grid[ny][nx] == 1:
                    neighbors.append((nx, ny, dx, dy))
            if neighbors:
                nx, ny, dx, dy = random.choice(neighbors)
                self.grid[ny][nx] = 0
                self.grid[y + dy//2][x + dx//2] = 0
                stack.append((nx, ny))
            else:
                stack.pop()
        self.grid[self.start[1]][self.start[0]] = 0
        self.grid[self.goal[1]][self.goal[0]] = 0

    def is_valid(self, x, y):
        return 0 <= x < self.width and 0 <= y < self.height and self.grid[y][x] == 0

    def get_neighbors(self, x, y):
        neighbors = []
        for dx, dy in [(0,1),(1,0),(0,-1),(-1,0)]:
            nx, ny = x + dx, y + dy
            if self.is_valid(nx, ny):
                neighbors.append((nx, ny))
        return neighbors

# ---------------- Agent Class ----------------
class Agent:
    def __init__(self, maze):
        self.maze = maze
        self.position = maze.start
        self.solution = []
        self.explored = set()
        self.path_index = 0
        self.solving = False

    def heuristic(self, a, b):
        return abs(a[0]-b[0]) + abs(a[1]-b[1])

    def a_star(self):
        self.explored.clear()
        start, goal = self.maze.start, self.maze.goal
        frontier = [(0, start, [start])]
        explored = set()
        while frontier:
            _, current, path = heapq.heappop(frontier)
            if current in explored: continue
            explored.add(current)
            self.explored.add(current)
            if current == goal:
                self.solution = path
                return
            for n in self.maze.get_neighbors(*current):
                if n not in explored:
                    new_path = path + [n]
                    priority = len(new_path) + self.heuristic(n, goal)
                    heapq.heappush(frontier, (priority, n, new_path))

    def reset(self):
        self.position = self.maze.start
        self.path_index = 0
        self.explored.clear()
        self.solution = []
        self.solving = False

# ---------------- Button Class ----------------
class Button:
    def __init__(self, rect, color, text):
        self.rect = pygame.Rect(rect)
        self.color = color
        self.text = text
        self.font = pygame.font.SysFont("Arial", 18)
    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)
        label = self.font.render(self.text, True, (255,255,255))
        screen.blit(label, (self.rect.x + 10, self.rect.y + 5))
    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

# ---------------- Main Game ----------------
def run_game():
    pygame.init()
    CELL = 30
    MAZE_W, MAZE_H = 20, 15
    WIDTH, HEIGHT = MAZE_W*CELL + 250, MAZE_H*CELL
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Interactive Maze Solver - AI Agent")

    maze = Maze(MAZE_W, MAZE_H)
    agent = Agent(maze)

    clock = pygame.time.Clock()
    speed = 8  # frames per second

    # Buttons
    solve_btn = Button((MAZE_W*CELL + 20, 20, 200, 30), (70,130,180), "Solve Maze")
    reset_btn = Button((MAZE_W*CELL + 20, 60, 200, 30), (180,70,70), "Reset Agent")
    newmaze_btn = Button((MAZE_W*CELL + 20, 100, 200, 30), (70,180,130), "New Maze")

    font = pygame.font.SysFont("Arial", 18)

    running = True
    while running:
        screen.fill((30,30,30))
        # Maze panel background
        pygame.draw.rect(screen, (40,40,40), (0,0, MAZE_W*CELL, MAZE_H*CELL))
        # Info panel
        pygame.draw.rect(screen, (50,50,50), (MAZE_W*CELL, 0, 250, HEIGHT))

        # Draw Maze
        for y in range(MAZE_H):
            for x in range(MAZE_W):
                color = (0,0,0) if maze.grid[y][x]==1 else (220,220,220)
                pygame.draw.rect(screen, color, (x*CELL, y*CELL, CELL, CELL))
                pygame.draw.rect(screen, (60,60,60), (x*CELL, y*CELL, CELL, CELL), 1)

        # Draw explored nodes (fade effect)
        for pos in agent.explored:
            pygame.draw.rect(screen, (100,100,255,180), (pos[0]*CELL+5, pos[1]*CELL+5, CELL-10, CELL-10))

        # Draw solution path
        if agent.solution:
            for i in range(len(agent.solution)-1):
                start = agent.solution[i]
                end = agent.solution[i+1]
                pygame.draw.line(screen, (255,215,0),
                                 (start[0]*CELL+CELL//2, start[1]*CELL+CELL//2),
                                 (end[0]*CELL+CELL//2, end[1]*CELL+CELL//2), 4)

        # Move agent along path
        if agent.solution and agent.path_index < len(agent.solution):
            agent.position = agent.solution[agent.path_index]
            agent.explored.add(agent.position)
            agent.path_index +=1

        # Draw start, goal, agent
        pygame.draw.rect(screen, (0,255,0), (maze.start[0]*CELL, maze.start[1]*CELL, CELL, CELL))
        pygame.draw.rect(screen, (255,0,0), (maze.goal[0]*CELL, maze.goal[1]*CELL, CELL, CELL))
        pygame.draw.circle(screen, (0,0,255), (agent.position[0]*CELL + CELL//2, agent.position[1]*CELL + CELL//2), CELL//3)

        # Draw Buttons
        solve_btn.draw(screen)
        reset_btn.draw(screen)
        newmaze_btn.draw(screen)

        # Info Panel
        info_texts = [
            f"Agent Status: {'Moving' if agent.path_index<len(agent.solution) else 'Solved'}",
            f"Steps Taken: {agent.path_index}",
            f"Path Length: {len(agent.solution)}",
            f"Explored Nodes: {len(agent.explored)}",
            f"Animation Speed: {speed} FPS"
        ]
        info_y = 150
        for text in info_texts:
            label = font.render(text, True, (255,255,255))
            screen.blit(label, (MAZE_W*CELL + 20, info_y))
            info_y += 30

        pygame.display.flip()
        clock.tick(speed)

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if solve_btn.is_clicked(event.pos):
                    agent.reset()
                    agent.a_star()
                elif reset_btn.is_clicked(event.pos):
                    agent.reset()
                elif newmaze_btn.is_clicked(event.pos):
                    maze = Maze(MAZE_W, MAZE_H)
                    agent = Agent(maze)
            elif event.type == pygame.KEYDOWN:
                # Adjust speed with UP/DOWN
                if event.key == pygame.K_UP: speed += 1
                elif event.key == pygame.K_DOWN: speed = max(1, speed-1)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    run_game()
