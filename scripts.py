import threading
from functools import partial
import lp_events, lp_colors, keyboard

COLOR_ACTIVE = lp_colors.GREEN
COLOR_PRIMED = lp_colors.PINK
COLOR_DEFAULT = lp_colors.BLUE

threads = [[None for y in range(9)] for x in range(9)]
running = False
to_run = []
text = [["" for y in range(9)] for x in range(9)]

def run_in_bg(func, x, y):
    global threads
    global to_run
    if not running:
        threads[x][y] = threading.Thread(None, func)
        threads[x][y].start()
    else:
        sto_run.append((func, x, y))

def run_funcs(funcs_in):
    global running
    global to_run
    running = True
    for f in funcs_in:
        f()
    running = False
    if len(to_run) > 0:
        tup = to_run.pop(0)
        func = tup[0]
        x = tup[1]
        y = tup[2]
        run_in_bg(func, x, y)
    threading.Timer(0.01, lp_colors.update, ()).start()

def run_script(script_str, x, y):
    script_lines = script_str.split('\n')
    funcs_to_run = []
    for line in script_lines:
        split_line = line.split(' ')
        if split_line[0] == "STRING":
            funcs_to_run.append(partial(keyboard.controller.type, (" ".join(split_line[1:]))))
        elif split_line[0] == "DELAY":
            funcs_to_run.append(partial(sleep, (float(split_line[1]))))
        elif split_line[0] == "TAP":
            funcs_to_run.append(partial(keyboard.tap, (split_line[1])))
        elif split_line[0] == "PRESS":
            funcs_to_run.append(partial(keyboard.controller.press, (split_line[1])))
        elif split_line[0] == "RELEASE":
            funcs_to_run.append(partial(keyboard.controller.release, (split_line[1])))
        elif split_line[0] == "SP_TAP":
            if keyboard.sp(split_line[1]) != None:
                funcs_to_run.append(partial(keyboard.tap, (keyboard.sp(split_line[1]))))
        elif split_line[0] == "SP_PRESS":
            if keyboard.sp(split_line[1]) != None:
                funcs_to_run.append(partial(keyboard.controller.press, (keyboard.sp(split_line[1]))))
        elif split_line[0] == "SP_RELEASE":
            if keyboard.sp(split_line[1]) != None:
                funcs_to_run.append(partial(keyboard.controller.release, (keyboard.sp(split_line[1]))))
    script_func = partial(run_funcs, (funcs_to_run))
    run_in_bg(script_func, x, y)

def bind(x, y, script_down, off_color=COLOR_DEFAULT):
    script_down_bindable = lambda a, b : run_script(script_down, x, y)
    lp_events.bind_func_with_colors(x, y, script_down_bindable, off_color, COLOR_ACTIVE)
    text[x][y] = script_down

def unbind(x, y):
    lp_events.unbind(x, y)
    threads[x][y] = None
    text[x][y] = ""