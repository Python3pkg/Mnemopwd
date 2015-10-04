# -*- coding: utf-8 -*-

# Copyright (C) 2015 Thierry Lemeunier <thierry at lemeunier dot net>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# ---------------------------------------------------------
# Singleton class

import hashlib
import base64
from pyelliptic.hash import hmac_sha512

def singleton(the_class):
    instances = {} # Dictionary of singleton objects
    def get_instance():
        if the_class not in instances:
            # Create a singleton object and store it
            instances[the_class] = the_class()
        return instances[the_class]
    return get_instance

# ---------------------------------------------------------
# Compute client id

def compute_client_id(ms, login):
    """Compute a client id according to the protocol"""
    ho = hashlib.sha256()
    ho.update(hmac_sha512(ms, ms + login))
    id = ho.digest()    
    return id # Return the client id

# ---------------------------------------------------------
# Compute client data filename

def compute_client_filename(id, ms, login):
    """Compute a filename"""    
    
    # Compute login hash
    ho = hashlib.sha256()
    ho.update(hmac_sha512(ms, login))
    hlogin = ho.digest()
    
    # Filename construction
    filename = (base64.b32encode(hlogin))[:52] + (base64.b32encode(id))[:52]
    
    return filename.decode() # Return client data filename (a string)

