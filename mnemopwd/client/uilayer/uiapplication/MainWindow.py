# -*- coding: utf-8 -*-

# Copyright (c) 2016, Thierry Lemeunier <thierry at lemeunier dot net>
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification,
# are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this
# list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
# this list of conditions and the following disclaimer in the documentation
# and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
# THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
# PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
# CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS;
# OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR
# OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
# ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import curses

from client.util.Configuration import Configuration
from client.util.funcutils import sfill
from client.uilayer.uicomponents.BaseWindow import BaseWindow
from client.uilayer.uicomponents.ButtonBox import ButtonBox
from client.uilayer.uiapplication.LoginWindow import LoginWindow
from client.uilayer.uiapplication.EditionWindow import EditionWindow
from client.uilayer.uiapplication.SearchWindow import SearchWindow
from client.uilayer.uiapplication.ApplicationMenu import ApplicationMenu
from client.uilayer.uiapplication.CreateMenu import CreateMenu


class MainWindow(BaseWindow):
    """
    The main window of the client application
    """

    def __init__(self, facade):
        """Create the window"""
        BaseWindow.__init__(self, None, curses.LINES - 2, curses.COLS, 0, 0)
        self.uifacade = facade  # Reference on ui layer facade
        self.connected = False  # Login state

        # Menu zone
        self.window.hline(1, 0, curses.ACS_HLINE, curses.COLS)
        message = "MnemoPwd Client v" + Configuration.version
        self.window.addstr(0, curses.COLS - len(message) - 1, message)
        self.window.addch(0, curses.COLS - len(message) - 3, curses.ACS_VLINE)
        self.window.addch(1, curses.COLS - len(message) - 3, curses.ACS_BTEE)
        self.window.refresh()

        self.applicationButton = ButtonBox(self, 0, 0, "MnemoPwd", shortcut='M')
        self.newButton = ButtonBox(self, 0, 11, "New", shortcut='N')
        self.searchButton = ButtonBox(self, 0, 17, "Search", shortcut='E')

        # Ordered list of shortcut keys
        self.shortcuts = ['M', 'N', 'E']

        # Ordered list of components
        self.items = [self.applicationButton, self.newButton, self.searchButton]

        # Edition window
        self.editscr = EditionWindow(self, curses.LINES - 4, int(curses.COLS * 2/3),
                                     2, int(curses.COLS * 1/3), "Edition", Configuration.btypes)

        # Search window
        self.searchscr = SearchWindow(self, curses.LINES - 4, int(curses.COLS * 1/3), 2, 0, "Search")

        # Status window
        self.statscr = curses.newwin(2, curses.COLS, curses.LINES - 2, 0)
        self.statscr.hline(0, 0, curses.ACS_HLINE, curses.COLS)
        self.statscr.refresh()

    def _get_credentials(self):
        """Get login/password"""
        self.update_status('Please start a connection')
        login, passwd = LoginWindow(self).start()
        if login is not False:
            self.uifacade.inform("connection.open.credentials", (login, passwd))
            self.window.addstr(1, 0, login+passwd)
            login = passwd = "                            "

    def _handle_block(self, number, idblock):
        """Start block edition"""
        # Change status message
        message = "Edit '" + ((Configuration.btypes[str(number)])["1"])["name"] + "' information block"
        self.update_status(message)

        # Prepare edition window
        if idblock is None:
            self.editscr.set_type(number)

        # Do edition
        result, values = self.editscr.start()

        # According to the result, save / update or delete or do nothing
        if result is True:
            self.uifacade.inform("application.editblock", (idblock, values))
            self.searchscr.do_search()  # Update search window
        elif values is True:
            self.uifacade.inform("application.deleteblock", idblock)
            self.searchscr.do_search()  # Update search window
        else:
            self.update_status('')

    def _search_block(self):
        """Start searching block"""
        self.searchscr.pre_search()
        return self.searchscr.start()

    def start(self, timeout=-1):
        # Get login/password
        self._get_credentials()

        while True:
            # Interaction loop
            result = BaseWindow.start(self)

            # Main menu
            if result == self.applicationButton:
                self.applicationButton.focus_off()
                result = ApplicationMenu(self, 2, 0, self.connected).start()
                if result == 'QUIT':
                    if self.connected:
                        self.uifacade.inform("connection.close", None)
                    break
                if result == 'LOGINOUT':
                    if not self.connected:
                        self._get_credentials()  # Try a connection
                    else:
                        self.uifacade.inform("connection.close", None)  # Disconnection

            # Create a new entry
            elif result == self.newButton:
                if self.connected:
                    self.newButton.focus_off()
                    result = CreateMenu(self, Configuration.btypes, 2, 9).start()
                    if result:
                        self._handle_block(result, None)
                else:
                    self.update_status('Please start a connection')

            # Search some entries
            elif result == self.searchButton:
                if self.connected:
                    self.searchButton.focus_off()
                    result, values = self._search_block()
                    if type(result) is int:
                        self._handle_block(int(values[0]), result)
                else:
                    self.update_status('Please start a connection')

    def update_window(self, key, value):
        """Update the main window content"""
        if key == "connection.state.login":
            self.connected = True
            self.update_status(value)
        if key == "connection.state.logout":
            self.connected = False
            self.update_status(value)
            self.editscr.clear_content()
            self.searchscr.clear_content()
        if key == "connection.state.error":
            self.connected = False
            self.update_status(value)
            self.editscr.clear_content()
            self.searchscr.clear_content()
            curses.flash()
        if key == "application.keyhandler":
            self.editscr.set_keyhandler(value)
        if key == "application.searchblock.result":
            self.searchscr.post_search(value)
        if key == "application.searchblock.oneresult":
            self.searchscr.add_a_result(*value)
        if key == "application.editionblock.seteditors":
            number, values = value
            self.editscr.set_type(number)
            self.editscr.set_infos(values)
        if key == "application.editionblock.cleareditors":
            self.editscr.clear_content()

    def update_load_bar(self, actual, maxi):
        import math
        max_len = curses.COLS - 15
        actual_len = int(actual * max_len / maxi)
        percent = str(math.floor(actual_len * 100 / max_len))
        message = sfill(actual_len, '█')
        currenty, currentx = curses.getsyx()  # Save current cursor position
        self.statscr.move(1, 7)
        self.statscr.clrtoeol()
        self.statscr.addstr(1, 8, percent + " %")  # Show percentage
        self.statscr.addstr(1, 14, message)  # Show load bar
        self.statscr.refresh()
        curses.setsyx(currenty, currentx)   # Set cursor position to saved position

    def update_status(self, value):
        """Update the status window content"""
        currenty, currentx = curses.getsyx() # Save current cursor position
        self.statscr.move(1, 1)
        self.statscr.clrtoeol()
        if self.connected:
            self.statscr.addstr("-O-")
        else:
            self.statscr.addstr("-||-")
        self.statscr.addch(0, 6, curses.ACS_TTEE)
        self.statscr.addch(1, 6, curses.ACS_VLINE)
        self.statscr.addstr(1, 8, value)
        self.statscr.refresh()
        curses.setsyx(currenty, currentx)   # Set cursor position to saved position

    def redraw(self):
        """See mother class"""
        self.editscr.redraw()
        self.searchscr.redraw()
        BaseWindow.redraw(self)
