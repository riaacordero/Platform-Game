"""
This module contains the game loop. It initializes, displays, and makes use of objects from the classes of
other modules. It contains functions that display each of the separate locations of the game, and a few variables that
help the functions and/or identify the current game state.
"""

from pygame.locals import *
from text import *
from level import *
from button import Button

pygame.init()
clock = pygame.time.Clock()

# Set screen
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Pixel Witch")

# Set music player
music_player = MusicPlayer()

# Create buttons
pause_btn = Button(450, 10, pause_img, pause_hov_img)

# Create texts
main_start_text = HoverableText(25, 335, "start", retro_gaming_font, 40, dark_gray, light_gray, gray)
main_exit_text = HoverableText(25, 400, "exit", retro_gaming_font, 40, dark_gray, light_gray, gray)

selection_text = Text(150, 150, "LEVEL SELECTION", fff_forward_font, 40, black)

over_text = Text(125, 300, "GAME OVER", fff_forward_font, 32, black)
over_restart_text = HoverableText(190, 385, "restart", retro_gaming_font, 24, dark_gray, light_gray, gray)
over_main_text = HoverableText(175, 420, "main menu", retro_gaming_font, 24, dark_gray, light_gray, gray)

clear_score_text = Text(250, 125, "0", fff_forward_font, 80, black, pos="center")
clear_text = Text(250, 210, "GAME CLEARED", fff_forward_font, 24, black, pos="center")
clear_next_text = HoverableText(250, 320, "next", retro_gaming_font, 32, dark_gray, light_gray, gray, pos="center")
clear_retry_text = HoverableText(250, 360, "retry", retro_gaming_font, 32, dark_gray, light_gray, gray, pos="center")
clear_main_text = HoverableText(250, 400, "main menu", retro_gaming_font, 32, dark_gray, light_gray, gray, pos="center")

pause_resume_text = HoverableText(250, 225, "resume", retro_gaming_font, 32, dark_gray, light_gray, gray, pos="center")
pause_main_text = HoverableText(250, 275, "main menu", retro_gaming_font, 32, dark_gray, light_gray, gray, pos="center")

score_text = Text(100, 10, "0", retro_gaming_font, 28, purple)

# Create text groups
main_menu_texts = TextGroup(main_start_text, main_exit_text)
level_selection_texts = TextGroup(selection_text)
game_over_texts = TextGroup(over_text, over_restart_text, over_main_text)
game_clear_texts = TextGroup(clear_text, clear_next_text, clear_retry_text, clear_main_text, clear_score_text)
pause_texts = TextGroup(pause_resume_text, pause_main_text)

# Create player
player = Player()

# Create levels
level_one = Level(level_one_data, player)

# Player state
current_player_state = PlayerState.ALIVE
player.reset(100, screen_height - 120, level_one)

# Game state
running = True
paused = False
pause_cooldown = 0

# Score display helper variables
score_display = 0
"""score to be displayed, which starts at 0 and ends with the total score"""
score_display_cooldown = fps // 2
"""waits for score_display_cooldown to be zero before score_display is shown"""
score_display_speed = fps // 10
"""changes score_display for every 1/score_display_speed seconds"""

# Location currently shown in screen
current_location = Location.MAIN_MENU


def display_main_menu():
    global running, current_location, current_player_state

    music_player.load_and_play(bgm_main_location, loops=-1, fade_ms=3000)
    screen.blit(bg_img, (0, 0))
    main_menu_texts.update()
    main_menu_texts.draw(screen)

    if main_exit_text.is_clicked():
        running = False
    elif main_start_text.is_clicked():
        music_player.stop_and_unload()
        current_location = Location.LEVEL_ONE
        level_one.reset()
        player.reset(100, screen_height - 130, level_one)
        current_player_state = player.player_state
        select_sfx.play()


def display_pause():
    global paused, pause_cooldown, current_location

    screen.blit(bg_img, (0, 0))
    pause_texts.update()
    pause_texts.draw(screen)

    if pause_texts.one_is_clicked():
        music_player.unpause()

    if pause_resume_text.is_clicked():
        paused = False
    if pause_main_text.is_clicked():
        music_player.stop_and_unload()
        paused = False
        current_location = Location.MAIN_MENU


def display_game_over(level: Level):
    global current_player_state, current_location

    screen.blit(bg_game_over_img, (0, 0))
    screen.blit(pygame.transform.scale(death_img, (200, 200)), (150, 50))
    game_over_texts.update()
    game_over_texts.draw(screen)

    if over_restart_text.is_clicked():
        level.reset()
        player.reset(100, screen_height - 130, level)
        current_player_state = player.player_state
    elif over_main_text.is_clicked():
        current_location = Location.MAIN_MENU


def display_game_clear(level: Level):
    global current_player_state, current_location, score_display, score_display_cooldown, score_display_speed

    screen.blit(bg_game_clear_img, (0, 0))
    if score_display_cooldown > 0:
        score_display_cooldown -= 1
    if score_display_speed > 0:
        score_display_speed -= 1
    if score_display_cooldown == 0 and score_display_speed == 0 and score_display != level.score:
        score_display_speed = fps // 10
        score_display += 1
        select_sfx.play()
    game_clear_texts.update()
    clear_score_text.update(str(score_display), pos="center", new_x=250, new_y=125)
    game_clear_texts.draw(screen, excluded=() if score_display == level.score else (clear_text,))

    if game_clear_texts.one_is_clicked():
        print(game_clear_texts.texts)
        score_display = 0
        score_display_cooldown = fps // 2
        score_display_speed = fps // 10

    if clear_next_text.is_clicked():
        pass
    elif clear_retry_text.is_clicked():
        level.reset()
        player.reset(100, screen_height - 130, level)
        current_player_state = player.player_state
    elif clear_main_text.is_clicked():
        current_location = Location.MAIN_MENU


def display_level(level: Level):
    global current_player_state, paused, score_display

    music_player.load_and_play(bgm_level_location, loops=-1, fade_ms=3000)
    if not paused:
        level.update()
        current_player_state = player.player_state
        level.draw(screen)
        screen.blit(key_img if player.has_key else key_inactive, (10, 10))
        screen.blit(gem_img, (55, 10))
        score_text.draw(screen)
        score_text.update(str(level.score))

    pause_btn.update()
    pause_btn.draw(screen)
    if pause_btn.is_clicked() and not paused:
        music_player.pause()
        paused = True
        cancel_sfx.play()
    if paused:
        display_pause()

    if current_player_state == PlayerState.LOST:
        music_player.stop_and_unload()
        display_game_over(level)
    elif current_player_state == PlayerState.WON:
        music_player.stop_and_unload()
        display_game_clear(level)


# GAME LOOP
if __name__ == "__main__":
    while running:

        clock.tick(fps)

        for event in pygame.event.get():
            if event.type == QUIT:
                running = False

        if current_location == Location.MAIN_MENU:
            display_main_menu()
        elif current_location == Location.LEVEL_ONE:
            display_level(level_one)

        pygame.display.update()
    pygame.quit()
