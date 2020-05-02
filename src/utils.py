def splitzero(string):
    if not isinstance(string, bytes):
        return bytes()

    char = b'\x00'
    if char not in string:
        return string
    return string.split(char)[0]

def getSectorPadding(bytesAmount, sectorsize):
    if bytesAmount % sectorsize == 0:
        return 0
    return sectorsize - (bytesAmount % sectorsize)


def readSectorFile(infilepath, sectorsize):
    infile = open(infilepath, 'rb')
    data = infile.read()
    infile.close()
    lenght = len(data)
    padding = getSectorPadding(lenght, sectorsize)
    return data.ljust(lenght + padding, b'\x00')