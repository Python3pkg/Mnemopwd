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

"""
State S21 : Login
"""

from client.util.funcutils import singleton
from client.corelayer.protocol.StateSCC import StateSCC

@singleton
class StateS21A(StateSCC):
    """State S21 : Login"""
        
    def do(self, handler, data):
        """Action of the state S21A: treat response of login request"""
        try:
            
            # Test challenge response
            if self.control_challenge(handler, data):
            
                # Test if login request is rejected
                is_KO = data[:5] == b"ERROR"
                if is_KO:
                    message = (data[6:]).decode()
                    raise Exception(message)
            
                # Test if login is accepted
                is_OK = data[:2] == b"OK"
                if is_OK:
                    # Notify the handler a property has changed
                    handler.loop.call_soon_threadsafe(handler.notify, "connection.state.login", "Connected to server")
        
        except Exception as exc:
            # Schedule a call to the exception handler
            handler.loop.call_soon_threadsafe(handler.exception_handler, exc)
        
        else:
            #handler.state = handler.states['31R'] # Next state
            pass
