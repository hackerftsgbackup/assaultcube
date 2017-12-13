# -*- coding: utf-8 -*-

"""
Copyright 2017 hackerftsg.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0
"""

import sys
import os.path
import ctypes
import ctypes.wintypes

sys.dont_write_bytecode = True

PROCESS_QUERY_INFORMATION = 0x0400
PROCESS_VM_OPERATION = 0x0008
PROCESS_VM_READ = 0x0010
PROCESS_VM_WRITE = 0x0020

MAX_PATH = 260


class ReadWriteMemory(object):
    """Class ReadWriteMemory"""

    def getprocessidbyname(self, pname):
        """Method getprocessidbyname"""
        pname += ".exe" if not pname.endswith(".exe") else ""

        processids, bytesreturned = self.enumprocesses()

        for index in list(range(int(bytesreturned / ctypes.sizeof(ctypes.wintypes.DWORD)))):
            processid = processids[index]
            hprocess = ctypes.windll.kernel32.OpenProcess(
                PROCESS_QUERY_INFORMATION, False, processid)
            if hprocess:
                imgname = (ctypes.c_char * MAX_PATH)()
                if ctypes.windll.psapi.GetProcessImageFileNameA(hprocess, imgname, MAX_PATH) >= 1:
                    filename = os.path.basename(imgname.value)
                    if filename.decode("utf-8") == pname:
                        return processid
                self.closehandle(hprocess)

    def enumprocesses(self):
        """Method enumprocesses"""
        count = 32
        while True:
            processids = (ctypes.wintypes.DWORD * count)()
            cb0 = ctypes.sizeof(processids)
            bytesreturned = ctypes.wintypes.DWORD()
            if ctypes.windll.Psapi.EnumProcesses(ctypes.byref(processids), cb0, ctypes.byref(bytesreturned)):
                if bytesreturned.value < cb0:
                    return processids, bytesreturned.value
                else:
                    count *= 2
            else:
                return None

    def openprocess(self, dwprocessid):
        """Method openprocess"""
        dwdesiredaccess = (PROCESS_QUERY_INFORMATION |
                           PROCESS_VM_OPERATION |
                           PROCESS_VM_READ |
                           PROCESS_VM_WRITE)
        binherithandle = False
        hprocess = ctypes.windll.kernel32.OpenProcess(
            dwdesiredaccess,
            binherithandle,
            dwprocessid)
        return hprocess if hprocess else None

    def closehandle(self, hprocess):
        """Method closehandle"""
        ctypes.windll.kernel32.CloseHandle(hprocess)
        return self.getlasterror()

    def getlasterror(self):
        """Method getlasterror"""
        return ctypes.windll.kernel32.GetLastError()

    def getpointer(self, hprocess, lpbaseaddress, offsets):
        """Method getpointer"""
        pointer = self.readprocessmemory(hprocess, lpbaseaddress)

        if offsets is None:
            return lpbaseaddress
        elif len(offsets) == 1:
            return int(str(pointer), 0) + int(str(offsets[0]), 0)
        else:
            count = len(offsets)
            for i in offsets:
                count -= 1
                pointer = self.readprocessmemory(
                    hprocess, int(str(pointer), 0) + int(str(i), 0))
                if count == 1:
                    break
            return pointer

    def readprocessmemory(self, hprocess, lpbaseaddress):
        """Method readprocessmemory"""
        try:
            readbuffer = ctypes.c_uint()
            lpbuffer = ctypes.byref(readbuffer)
            nsize = ctypes.sizeof(readbuffer)
            lpnumberofbytesread = ctypes.c_ulong(0)

            ctypes.windll.kernel32.ReadProcessMemory(
                hprocess,
                lpbaseaddress,
                lpbuffer,
                nsize,
                lpnumberofbytesread)
            return readbuffer.value
        except (BufferError, ValueError, TypeError):
            self.closehandle(hprocess)
            return "ERROR Handle Closed", hprocess, self.getlasterror()

    def writeprocessmemory(self, hprocess, lpbaseaddress, value):
        """Method writeprocessmemory"""
        try:
            writebuffer = ctypes.c_uint(value)
            lpbuffer = ctypes.byref(writebuffer)
            nsize = ctypes.sizeof(writebuffer)
            lpnumberofbytesread = ctypes.c_ulong(0)

            ctypes.windll.kernel32.WriteProcessMemory(
                hprocess,
                lpbaseaddress,
                lpbuffer,
                nsize,
                lpnumberofbytesread)
        except (BufferError, ValueError, TypeError):
            self.closehandle(hprocess)
            return "ERROR Handle Closed", hprocess, self.getlasterror()


RWM = ReadWriteMemory()
