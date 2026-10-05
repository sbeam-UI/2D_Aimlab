
#include<bits/stdc++.h>
import pygame
import random
import sys

pygame.init()
pygame.key.stop_text_input()

WIDTH, HEIGHT = 1200, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("2D练枪器")
clock = pygame.time.Clock()

# 字体
font_path = r"C:/Windows/Fonts/simhei.ttf"
try:
    font = pygame.font.Font(font_path, 36)
    small_font = pygame.font.Font(font_path, 28)
    tip_font = pygame.font.Font(font_path, 22)
except Exception:
    print("警告：无黑体，中文方框")
    font = pygame.font.Font(None, 36)
    small_font = pygame.font.Font(None, 28)
    tip_font = pygame.font.Font(None, 22)

# 状态
STATE_MENU = 0
STATE_SETTINGS = 1
STATE_GAME = 2
STATE_RESULT = 3
game_state = STATE_MENU

MODES = {
    "Microshot": "微小移动靶，打中即换位，其他靶不动",
    "Popcorn": "多靶同时存在，击中单个立即刷新该靶"
}
mode_list = list(MODES.keys())
selected_mode = "Popcorn"

settings = {
    "crosshair_style": 0,
    "cross_r": 255,
    "cross_g": 255,
    "cross_b": 255,
    "cross_size": 12,
    "target_size": 22,
    "train_time": 30,
    "target_speed": 120,
    "popcorn_count": 3,
    "microshot_count":3
}

class Target:
    def __init__(self, mode):
        self.radius = settings["target_size"]
        margin = self.radius + 20
        self.x = random.randint(margin, WIDTH - margin)
        self.y = random.randint(margin, HEIGHT - margin)
        self.mode = mode
        self.spawn_time = pygame.time.get_ticks()
        self.life_time = 1800
        self.vx = random.choice([-1,1]) * random.uniform(settings["target_speed"]*0.3, settings["target_speed"])
        self.vy = random.choice([-1,1]) * random.uniform(settings["target_speed"]*0.3, settings["target_speed"])

    def update(self, dt):
        if self.mode == "Popcorn":
            return
        self.x += self.vx * dt
        self.y += self.vy * dt
        if self.x - self.radius < 0 or self.x + self.radius > WIDTH:
            self.vx *= -1
        if self.y - self.radius < 0 or self.y + self.radius > HEIGHT:
            self.vy *= -1

    def draw(self):
        pygame.draw.circle(screen, (255,70,70), (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(screen, (255,255,255), (int(self.x), int(self.y)), self.radius//2)

    def is_expired(self):
        if self.mode == "Popcorn":
            return False
        return pygame.time.get_ticks() - self.spawn_time > self.life_time

    def hit_check(self, mx, my):
        dx = mx - self.x
        dy = my - self.y
        return dx*dx + dy*dy <= self.radius * self.radius

def draw_crosshair(mx, my):
    cr = settings["cross_r"]
    cg = settings["cross_g"]
    cb = settings["cross_b"]
    size = settings["cross_size"]
    style = settings["crosshair_style"]
    color = (cr, cg, cb)

    if style == 0:
        # 十字准星
        pygame.draw.line(screen, color, (mx - size, my), (mx + size, my), 2)
        pygame.draw.line(screen, color, (mx, my - size), (mx, my + size), 2)
    elif style == 1:
        # 圆点准星
        pygame.draw.circle(screen, color, (mx, my), 4)
    elif style == 2:
        # 空心圆环 + 十字向外伸出
        pygame.draw.circle(screen, color, (mx, my), size, 2)
        line_len = size + 6
        pygame.draw.line(screen, color, (mx - line_len, my), (mx + line_len, my), 2)
        pygame.draw.line(screen, color, (mx, my - line_len), (mx, my + line_len), 2)

class Slider:
    def __init__(self, x,y,w,h, minv, maxv, val_key):
        self.rect = pygame.Rect(x,y,w,h)
        self.minv = minv
        self.maxv = maxv
        self.key = val_key
        self.val = settings[val_key]
        self.dragging = False

    def sync_from_settings(self):
        self.val = settings[self.key]

    def draw(self):
        pygame.draw.rect(screen, (70,70,70), self.rect, border_radius=4)
        ratio = (self.val - self.minv)/(self.maxv-self.minv)
        cx = self.rect.x + ratio * self.rect.w
        pygame.draw.circle(screen, (220,220,220), (int(cx), self.rect.centery), 10)

# 滑块
sliders = {
    "cross_r": Slider(420, 80, 240, 20, 0, 255, "cross_r"),
    "cross_g": Slider(420, 125, 240, 20, 0, 255, "cross_g"),
    "cross_b": Slider(420, 170, 240, 20, 0, 255, "cross_b"),
    "cross_size": Slider(420, 215, 240, 20, 4, 30, "cross_size"),
    "target_size": Slider(420, 260, 240, 20, 8, 60, "target_size"),
    "train_time": Slider(420, 305, 240, 20, 10, 120, "train_time"),
    "target_speed": Slider(420, 350, 240, 20, 0, 300, "target_speed"),
    "popcorn_count": Slider(420, 395, 240, 20, 1, 8, "popcorn_count"),
    "microshot_count": Slider(420, 440, 240, 20, 1, 8, "microshot_count"),
}

btn_setting_rect = pygame.Rect(0,0,220,60)
btn_start_rect = pygame.Rect(0,0,220,60)
btn_back_menu = pygame.Rect(0,0,200,50)
btn_quit_program = pygame.Rect(0,0,200,50)

def draw_menu():
    screen.fill((30,30,30))
    title = font.render("练枪器 - 主菜单", True, (255,255,255))
    screen.blit(title, (WIDTH//2-title.get_width()//2,60))

    for idx, m in enumerate(mode_list):
        text_str = f"{idx+1}. {m} : {MODES[m]}"
        # 选中的模式高亮黄色，其余浅灰
        if m == selected_mode:
            text = font.render(text_str, True, (255, 220, 60))
        else:
            text = font.render(text_str, True, (220,220,220))
        y_pos = 140 + idx*50
        screen.blit(text, (WIDTH//2-text.get_width()//2, y_pos))

    # 主菜单按钮
    btn_setting_rect.center = (WIDTH//2, 320)
    btn_start_rect.center = (WIDTH//2, 420)

    pygame.draw.rect(screen, (60,90,140), btn_setting_rect, border_radius=8)
    txt_set = font.render("设置面板 (S)", True, (255,255,255))
    screen.blit(txt_set, (btn_setting_rect.centerx - txt_set.get_width()//2, btn_setting_rect.centery - txt_set.get_height()//2))

    pygame.draw.rect(screen, (40,140,80), btn_start_rect, border_radius=8)
    txt_start = font.render("开始训练 (空格)", True, (255,255,255))
    screen.blit(txt_start, (btn_start_rect.centerx - txt_start.get_width()//2, btn_start_rect.centery - txt_start.get_height()//2))

    hint2 = small_font.render("↑↓切换训练模式 | C切换准星", True, (160,160,160))
    screen.blit(hint2, (WIDTH//2-hint2.get_width()//2, 480))

def draw_settings():
    screen.fill((30,30,30))
    title = font.render("设置面板", True, (255,255,255))
    screen.blit(title, (WIDTH//2-title.get_width()//2, 20))

    labels = [
        ("准星红色 R", sliders["cross_r"]),
        ("准星绿色 G", sliders["cross_g"]),
        ("准星蓝色 B", sliders["cross_b"]),
        ("准星大小", sliders["cross_size"]),
        ("靶子大小", sliders["target_size"]),
        ("训练时长(秒)", sliders["train_time"]),
        ("靶移动速度", sliders["target_speed"]),
        ("Popcorn靶数量", sliders["popcorn_count"]),
        ("Microshot靶数量", sliders["microshot_count"]),
    ]
    text_y = 80
    for txt, sld in labels:
        t = small_font.render(f"{txt}: {sld.val:.1f}", True, (230,230,230))
        screen.blit(t, (120, text_y))
        sld.draw()
        text_y += 45

    style_txt = small_font.render(f"准星样式(0十字,1圆点,2圆环+十字): {settings['crosshair_style']}", True, (230,230,230))
    screen.blit(style_txt, (120, text_y + 10))

    preview_txt = small_font.render("准星预览：", True, (230,230,230))
    screen.blit(preview_txt, (120, text_y + 50))
    draw_crosshair(320, text_y + 100)

    tip1 = tip_font.render("提示：0=十字｜1=圆点｜2=圆环+向外十字", True, (200,200,200))
    tip2 = tip_font.render("拖动滑块修改参数，ESC返回主菜单，C切换准星", True, (200,200,200))
    screen.blit(tip1, (600, 80))
    screen.blit(tip2, (600, 110))

    # 设置面板按钮
    btn_back_menu.center = (WIDTH//2 - 140, 620)
    pygame.draw.rect(screen, (60,90,140), btn_back_menu, border_radius=8)
    back_text = small_font.render("返回菜单", True, (255,255,255))
    screen.blit(back_text, (btn_back_menu.centerx-back_text.get_width()//2, btn_back_menu.centery-back_text.get_height()//2))

    btn_quit_program.center = (WIDTH//2 + 140, 620)
    pygame.draw.rect(screen, (180,40,40), btn_quit_program, border_radius=8)
    quit_text = small_font.render("退出程序", True, (255,255,255))
    screen.blit(quit_text, (btn_quit_program.centerx-quit_text.get_width()//2, btn_quit_program.centery-quit_text.get_height()//2))

def draw_game(time_left, targets, score, hits, shots, mx, my):
    screen.fill((20,20,20))
    for t in targets:
        t.draw()
    draw_crosshair(mx, my)
    hud1 = font.render(f"时间: {time_left:.1f}s | 得分:{score}", True, (255,255,255))
    hud2 = font.render(f"命中率: {100*hits/shots:.1f}%" if shots>0 else "命中率: 0%", True, (220,220,220))
    hud3 = font.render(f"靶数量: {len(targets)}", True, (200,200,0))
    hud4 = font.render(f"准星样式: {settings['crosshair_style']}", True, (180,180,180))
    screen.blit(hud1, (20,20))
    screen.blit(hud2, (20,60))
    screen.blit(hud3, (20,100))
    screen.blit(hud4, (20,140))
    esc_hint = small_font.render("ESC 退出训练 | C切换准星", True, (160,160,160))
    screen.blit(esc_hint, (WIDTH-320, 20))

def draw_result(score, hits, shots):
    screen.fill((30,30,30))
    t1 = font.render("训练结束", True, (255,255,255))
    acc = 100*hits/shots if shots>0 else 0
    t2 = font.render(f"得分: {score}", True, (255,210,80))
    t3 = font.render(f"命中: {hits} / {shots}  命中率: {acc:.1f}%", True, (220,220,220))
    t4 = font.render("ESC 返回主菜单", True, (180,180,180))
    screen.blit(t1,(WIDTH//2-t1.get_width()//2,100))
    screen.blit(t2,(WIDTH//2-t2.get_width()//2,180))
    screen.blit(t3,(WIDTH//2-t3.get_width()//2,240))
    screen.blit(t4,(WIDTH//2-t4.get_width()//2,320))

def main():
    global game_state, selected_mode
    targets = []
    score = hits = shots = 0
    start_time = pygame.time.get_ticks()

    running = True
    while running:
        dt = clock.tick(144)/1000.0
        mx, my = pygame.mouse.get_pos()

        if game_state == STATE_GAME:
            pygame.mouse.set_visible(False)
        else:
            pygame.mouse.set_visible(True)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_c:
                    settings["crosshair_style"] = (settings["crosshair_style"] + 1) % 3
                    print(f"✅ C按下！准星切换到 {settings['crosshair_style']}")

                if event.key == pygame.K_ESCAPE:
                    game_state = STATE_MENU

                if game_state == STATE_MENU:
                    if event.key == pygame.K_s:
                        game_state = STATE_SETTINGS
                        for s in sliders.values():
                            s.sync_from_settings()
                    if event.key == pygame.K_SPACE:
                        game_state = STATE_GAME
                        targets.clear()
                        if selected_mode == "Popcorn":
                            count = int(settings["popcorn_count"])
                            for i in range(count):
                                new_t = Target("Popcorn")
                                targets.append(new_t)
                        else:
                            count = int(settings["microshot_count"])
                            for i in range(count):
                                new_t = Target("Microshot")
                                targets.append(new_t)
                        score = hits = shots = 0
                        start_time = pygame.time.get_ticks()
                    if event.key == pygame.K_UP:
                        idx = mode_list.index(selected_mode)
                        selected_mode = mode_list[(idx-1)%len(mode_list)]
                    if event.key == pygame.K_DOWN:
                        idx = mode_list.index(selected_mode)
                        selected_mode = mode_list[(idx+1)%len(mode_list)]

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if game_state == STATE_MENU:
                    if btn_setting_rect.collidepoint(event.pos):
                        game_state = STATE_SETTINGS
                        for s in sliders.values():
                            s.sync_from_settings()
                    elif btn_start_rect.collidepoint(event.pos):
                        game_state = STATE_GAME
                        targets.clear()
                        if selected_mode == "Popcorn":
                            count = int(settings["popcorn_count"])
                            for i in range(count):
                                new_t = Target("Popcorn")
                                targets.append(new_t)
                        else:
                            count = int(settings["microshot_count"])
                            for i in range(count):
                                new_t = Target("Microshot")
                                targets.append(new_t)
                        score = hits = shots = 0
                        start_time = pygame.time.get_ticks()

                elif game_state == STATE_SETTINGS:
                    if btn_back_menu.collidepoint(event.pos):
                        game_state = STATE_MENU
                    elif btn_quit_program.collidepoint(event.pos):
                        running = False
                    else:
                        for s in sliders.values():
                            if s.rect.collidepoint(event.pos):
                                s.dragging = True

                elif game_state == STATE_GAME:
                    shots += 1
                    hit = False
                    for idx in range(len(targets)):
                        t = targets[idx]
                        if t.hit_check(mx, my):
                            hit = True
                            hits += 1
                            score += 100

                            if selected_mode == "Popcorn":
                                targets.pop(idx)
                                targets.append(Target("Popcorn"))
                            elif selected_mode == "Microshot":
                                t.x = random.randint(t.radius + 20, WIDTH - t.radius - 20)
                                t.y = random.randint(t.radius + 20, HEIGHT - t.radius - 20)
                                t.spawn_time = pygame.time.get_ticks()
                                t.vx = random.choice([-1, 1]) * random.uniform(settings["target_speed"] * 0.3, settings["target_speed"])
                                t.vy = random.choice([-1, 1]) * random.uniform(settings["target_speed"] * 0.3, settings["target_speed"])
                            break
                    if not hit:
                        score -= 5

            if event.type == pygame.MOUSEBUTTONUP and event.button ==1:
                if game_state == STATE_SETTINGS:
                    for s in sliders.values():
                        if s.dragging:
                            s.dragging = False
                            s.val = round(s.val, 1)
                            settings[s.key] = s.val

            if event.type == pygame.MOUSEMOTION:
                if game_state == STATE_SETTINGS:
                    for s in sliders.values():
                        if s.dragging:
                            nx = max(s.rect.x, min(event.pos[0], s.rect.x + s.rect.w))
                            r = (nx - s.rect.x)/s.rect.w
                            s.val = s.minv + r*(s.maxv-s.minv)
                            settings[s.key] = s.val

        # 游戏更新
        if game_state == STATE_GAME:
            elapsed = (pygame.time.get_ticks() - start_time)/1000.0
            time_left = settings["train_time"] - elapsed
            if time_left <=0:
                game_state = STATE_RESULT

            for t in targets[:]:
                t.update(dt)
                if t.is_expired():
                    targets.remove(t)
                    targets.append(Target("Microshot"))

            draw_game(time_left, targets, score, hits, shots, mx, my)
        elif game_state == STATE_MENU:
            draw_menu()
        elif game_state == STATE_SETTINGS:
            draw_settings()
        elif game_state == STATE_RESULT:
            draw_result(score, hits, shots)

        pygame.display.flip()
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
