# -*- coding: utf-8 -*-

"""
Copyright 2017 hackerftsg.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0
"""

import sys
from Scripts.ReadWriteMemory import RWM

sys.dont_write_bytecode = True


class AssaultCube(object):
    """Class AssaultCube"""

    def __init__(self, pname):
        self.pname = pname
        self.processid = RWM.getprocessidbyname(self.pname)
        self.hprocess = RWM.openprocess(self.processid)

        found = bool(self.hprocess)
        if not found:
            exit("ERRO Jogo nao encontrado!")
        else:
            self.address_health = RWM.getpointer(
                self.hprocess, 0x004e4dbc, offsets=[0xf4])
            self.address_ammo = RWM.getpointer(
                self.hprocess, 0x004df73c, offsets=[0x378, 0x14, 0x0])
            self.address_grenade = RWM.getpointer(
                self.hprocess, 0x004df73c, offsets=[0x35c, 0x14, 0x0])

    def health(self, ammount):
        """Method health"""
        RWM.writeprocessmemory(self.hprocess, self.address_health, ammount)
        return "OK Agora voce tem %d de vida!" % ammount

    def ammo(self, ammount):
        """Method ammo"""
        RWM.writeprocessmemory(self.hprocess, self.address_ammo, ammount)
        return "OK Agora voce tem %d de municao!" % ammount

    def grenade(self, ammount):
        """Method grenade"""
        RWM.writeprocessmemory(self.hprocess, self.address_grenade, ammount)
        return "OK Agora voce tem %d granadas!" % ammount


if __name__ == "__main__":
    try:
        ASSAULTCUBE = AssaultCube("ac_client")
        print >> sys.stderr, ASSAULTCUBE.health(int(raw_input("VIDA: ")))
        print >> sys.stderr, ASSAULTCUBE.ammo(int(raw_input("MUNICAO: ")))
        print >> sys.stderr, ASSAULTCUBE.grenade(int(raw_input("GRANADAS: ")))
    except ValueError:
        exit("ERRO ValueError")
