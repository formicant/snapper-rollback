from __future__ import annotations
from typing import Callable
from textwrap import wrap
import curses


_select_keys = { ord(' '), ord('\n') }    # Space, Enter
_back_keys = { curses.KEY_BACKSPACE, 27 } # BackSpace, Esc


def _wrap_text(text: list[str], width: int) -> list[str]:
    lines = []
    for paragraph in text:
        if paragraph == '':
            lines.append('')
        else:
            wrapped = wrap(paragraph, width, subsequent_indent='  ')
            lines.extend(wrapped)
    return lines


class UI:
    def __init__(self, title: str, function: Callable[[UI], None]):
        def wrapper(screen: curses.window):
            self.screen = screen
            self.height, self.width = screen.getmaxyx()
            curses.set_escdelay(1)
            curses.curs_set(False)
            screen.clear()
            function(self)
        
        self.title = title
        curses.wrapper(wrapper)

    def _add_header(self) -> None:
        header = self.screen.subwin(1, self.width, 0, 0)
        header.bkgd(' ', curses.A_REVERSE)
        header.addstr(0, 1, f'{self.title[:self.width - 2]:^{self.width - 2}}')
        header.refresh()

    def _add_selection_list(self,
            y: int, x: int,
            height: int, width: int,
            items: list[str],
            default_index: int
    ) -> int|None:
        item_count = len(items)
        if item_count == 0:
            self.screen.addstr(y, x, ' (no items) ')
            while self.screen.getch() not in _back_keys:
                pass
            return None
        
        pad = curses.newpad(item_count, width + 1)
        # width + 1 to prevent issue with the last line
        
        def write_item(i: int, selected: bool=False) -> None:
            attr = curses.A_REVERSE if selected else curses.A_NORMAL
            pad.addstr(i, 0, f' {items[i]:.{width - 2}} ', attr)
        
        for i in range(item_count):
            write_item(i)
        
        index = default_index
        position = 0
        
        while True:
            if height == 1:
                position = index
            elif index < position + 1:
                position = max(0, index - 1)
            elif index > position + height - 2:
                position = min(item_count - height, index - height + 2)
            
            write_item(index, selected=True)
            pad.refresh(position, 0, y, x, y + height - 1, x + width - 1)
            write_item(index, selected=False)
            
            key = self.screen.getch()
            if key == curses.KEY_UP:
                index = max(0, index - 1)
            elif key == curses.KEY_DOWN:
                index = min(item_count - 1, index + 1)
            elif key == curses.KEY_PPAGE:
                index = max(0, index - height)
            elif key == curses.KEY_NPAGE:
                index = min(item_count - 1, index + height)
            elif key == curses.KEY_HOME:
                index = 0
            elif key == curses.KEY_END:
                index = item_count - 1
            elif key in _select_keys:
                return index
            elif key in _back_keys:
                return None
    
    def show_selection_page(self,
            text: list[str],
            items: list[str],
            default_index: int=0
    ) -> int|None:
        self.screen.clear()
        self._add_header()
        text_lines = _wrap_text(text, self.width - 2)
        for i, line in enumerate(text_lines):
            self.screen.addstr(2 + i, 1, line)
        self.screen.refresh()
        top = len(text_lines) + 3
        return self._add_selection_list(
            top, 1, self.height - top, self.width - 2,
            items, default_index
        )
