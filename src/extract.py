from PIL import Image
from errorpixel import lowPixelHasError, midPixelHasError

def get_bit(value, bitpositon):
    return (value >> bitpositon) & 1

def parse_secret_key(secretKeyPath):
    f = open(secretKeyPath, "r")
    secret_key = f.read()
    f.close()

    pixel_positions = [tuple(map(int, x.split(','))) for x in secret_key.split(';')]
    return pixel_positions

def parse_sdb0coordinate(sdb0coordinatePath):
    f = open(sdb0coordinatePath, "r")
    sdb0coordinate = f.read()
    f.close()

    sdb0coordinate = [tuple(map(int, x.split(','))) for x in sdb0coordinate.split(';')]
    return sdb0coordinate

def extract_algorithm(stegoImagePath, pixelPositions, t1, t2, sdb0coordinate, log_file):
    sdb = []
    stegoImage = Image.open(stegoImagePath).convert("L")
    
    index = 0
    for pixelPos in pixelPositions:
        pixelValue = stegoImage.getpixel(pixelPos)
        if pixelValue < t1:
            if pixelValue in lowPixelHasError and pixelPos in sdb0coordinate:
                sdb.append(0)
                log_file.write(f"index: {index:<5} pixVal: {pixelValue:<5} inserted: {bit}\n")
            else:
                bit = get_bit(pixelValue, 2)
                sdb.append(bit)
                log_file.write(f"index: {index:<5} pixVal: {pixelValue:<5} inserted: {bit}\n")
            index += 1
        elif pixelValue >= t1 and pixelValue < t2:
            if pixelValue in midPixelHasError and pixelPos in sdb0coordinate:
                sdb.append(0)
                log_file.write(f"index: {index:<5} pixVal: {pixelValue:<5} inserted: {bit}\n")
            else:
                bit = get_bit(pixelValue, 1)
                sdb.append(bit)
                log_file.write(f"index: {index:<5} pixVal: {pixelValue:<5} inserted: {bit}\n")
            index += 1
        else:
            bit = get_bit(pixelValue, 0)
            sdb.append(bit)
            log_file.write(f"index: {index:<5} pixVal: {pixelValue:<5} inserted: {bit}\n")
            index += 1
    return sdb


secretPath = "data/secret_key.txt"
stegoPath = "img/stg/axial2_stg.bmp"
sdb0coordinate_path = "data/sdb0pos.txt"
sdb0coordinates = parse_sdb0coordinate(sdb0coordinate_path)
pixel_positions = parse_secret_key(secretPath)
t1 = 86
t2 = 171

with open("data/log_extract.txt", "w") as log_file:
    sdb = extract_algorithm(stegoPath, pixel_positions, t1, t2, sdb0coordinates, log_file)

# print extracted data seperated with whitespaces every 8 bits
result = []
for i in range(0, len(sdb), 8):
    result.append(''.join(map(str, sdb[i:i+8])))   

res_string = ' '.join(result)
with open('data/result.txt', 'w') as f:
    f.write(res_string)