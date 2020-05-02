import struct
from utils import *

class IMGArchive:
    sectorsize = 2048
    headersize = 8
    dentrysize = 32

    
    def __init__(self, filepath, callback=None):
        self.filestream = open(filepath, 'rb')
        self.__loadHeader()
        self.__loadDentries()
        self.__loadData(callback)


    def __del__(self):
        self.filestream.close()


    def find(self, needle):
        for dentry in self.dentries:
            if needle in dentry['snme']:
                print(
                    dentry['ofst'],
                    dentry['strm'],
                    dentry['snme']
                )

    def replace(self, name, infilepath):
        idx, dentry = self.getDentryByName(name)
        if dentry == {}: return

        data = readSectorFile(infilepath, self.sectorsize)
        if not data: return

        oldstrm = dentry['strm']
        dentry['strm'] = len(data) // self.sectorsize
        dentry['data'] = data

        toupdate = [d for i,d in enumerate(self.dentries) if i > idx]
        for item in toupdate:
            item['ofst'] += dentry['strm'] - oldstrm


    def extract(self, name, outfilepath):
        idx, dentry = self.getDentryByName(name)
        if dentry == {}: return
        
        outfile = open(outfilepath, 'wb')
        outfile.write(dentry['data'])
        outfile.close()

        
    def save(self, filepath, callback=None):
        open(filepath, 'wb').close()
        written = 0
        archive = open(filepath, 'ab')

        written += archive.write(struct.pack(
            '4sI',
            self.version,
            self.nentries
            ))
            
        for dentry in self.dentries:
            written += archive.write(struct.pack(
                'IHH24s',
                dentry['ofst'],
                dentry['strm'],
                dentry['size'],
                dentry['name']
            ))
        
        padding = getSectorPadding(written, self.sectorsize)
        archive.write(b'\x00' * padding)

        status = callable(callback)  
        for i, dentry in enumerate(self.dentries):
            archive.write(dentry['data'])
            if status and i % 500 == 0:
                callback(i, self.nentries)
        if status:
            callback(0, 0)
        
        archive.close()
        
        
    def getDentryByName(self, name):
        for i in range(self.nentries):
            if name == self.dentries[i]['snme']:
                return i, self.dentries[i]
        return -1, {}

    def getDentries(self):
        return self.dentries

    def getNentries(self):
        return self.nentries

    def getSectorsize(self):
        return self.sectorsize
        
    def __loadHeader(self):
        self.filestream.seek(0,0)
        data = self.filestream.read(self.headersize)
        self.version, self.nentries = struct.unpack('4sI', data)

    def __loadDentries(self):
        self.filestream.seek(self.headersize, 0)
        self.dentries = []
        for _ in range(self.nentries):
            data = self.filestream.read(self.dentrysize)
            offset, streaming, size, name = struct.unpack('IHH24s', data)
            self.dentries.append(
                {
                    'ofst' : offset,
                    'strm' : streaming,
                    'size' : size,
                    'name' : name,
                    'snme' : splitzero(name).decode(),
                    'data' : ''
                }
            )

    def __loadData(self, callback=None):
        status = callable(callback)
        for i, dentry in enumerate(self.dentries):
            offset = dentry['ofst'] * self.sectorsize
            toread = dentry['strm'] * self.sectorsize
            self.filestream.seek(offset, 0)
            dentry['data'] = self.filestream.read(toread)
            
            if status and i % 500 == 0:
                callback(i, self.nentries)

        if status:
            callback(0, 0)