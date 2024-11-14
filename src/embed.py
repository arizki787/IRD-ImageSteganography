from PIL import Image
import random
import math
import numpy as np
from skimage.metrics import structural_similarity as ssim
#calculate bytes available in host image for modification
def get_available_capacity(coverImagePath):
    coverImage = Image.open(coverImagePath)
    coverImageSize = coverImage.size
    coverImageWidth = coverImageSize[0]
    coverImageHeight = coverImageSize[1]
    coverImageCapacity = coverImageWidth * coverImageHeight * 8
    return coverImageCapacity

#extract secret data bits from secret data file (assuming the secret data is already in bits)
def secret_data_bits(secretDataPath):
    with open(secretDataPath, 'r') as secretDataFile:
        secretData = secretDataFile.read().strip()
    # Remove white spaces and convert to a list of bits
    secretDataBits = list(secretData.replace(" ", "").replace("\t", "").replace("\n", ""))
    return secretDataBits

#check if host image capacity is less than or equal to SDB size
def check_capacity(coverImagePath, secretDataPath):
    coverImageCapacity = get_available_capacity(coverImagePath)
    secretDataBits = len(secret_data_bits(secretDataPath))
    return coverImageCapacity >= secretDataBits

#embed secret data into host image
def get_unique_random_pixel_positions(image_path, sdb_length):
    # Buka host image
    image = Image.open(image_path).convert("L")
    width, height = image.size
    
    # Gunakan set untuk memastikan piksel yang dipilih tidak duplikat
    selected_pixels = set()
    
    # Pilih koordinat piksel secara acak dan pastikan tidak ada duplikasi
    while len(selected_pixels) < sdb_length:
        x = random.randint(0, width - 1)
        y = random.randint(0, height - 1)
        selected_pixels.add((x, y))
    
    # Kembalikan sebagai list jika diperlukan
    return list(selected_pixels)

def create_secret_key(pixel_positions):
    # Generate a secret key from pixel positions
    secret_key = ';'.join([f"{x},{y}" for x, y in pixel_positions])
    return secret_key

def sdb0pos(sdb0poslist, sdb0post_path):
    sdb0coordinate = ';'.join([f"{x},{y}" for x, y in sdb0poslist])
    f = open(sdb0post_path, "w")
    f.write(sdb0coordinate)
    f.close()
    return True

def embedding_algorithm(coverImagePath, secretDataPath, pixelPosition, t1, t2, stegoImagePath, sdb0pos_path, log_file):
    # Coordinate of pixels that embedded with 0
    sdb0posList = []
    # Check if host image capacity is less than or equal to SDB size
    if not check_capacity(coverImagePath, secretDataPath):
        return False
    # Embed secret data into host image
    stegoImage = Image.open(coverImagePath).convert("L")
    
    sdbIndex = 0
    sdb = secret_data_bits(secretDataPath)
    for pixelPos in pixelPosition:
        # Get pixel value
        pixelValue = stegoImage.getpixel(pixelPos)
        # Get secret data bit
        if pixelValue < t1:
            # Get the hold value
            hold = pixelValue & 0b00000111
            if hold <= 3 and sdb[sdbIndex] == '0':
                log_file.write(f"pixVal before : {pixelValue}\t\t ")
                pixelValue = pixelValue | hold
                stegoImage.putpixel(pixelPos, pixelValue)
                sdb0posList.append(pixelPos)
                log_file.write(f"inserted : {pixelValue}\t\tindex : {sdbIndex}\n")
                sdbIndex += 1
            elif hold <= 3 and sdb[sdbIndex] == '1':
                log_file.write(f"pixVal before : {pixelValue}\t\t ")
                pixelValue = pixelValue | 0b00000111
                pixelValue = pixelValue - 3
                stegoImage.putpixel(pixelPos, pixelValue)
                log_file.write(f"inserted : {pixelValue}\t\tindex : {sdbIndex}\n")
                sdbIndex += 1
            elif hold > 3 and sdb[sdbIndex] == '1':
                log_file.write(f"pixVal before : {pixelValue}\t\t ")
                pixelValue = pixelValue | hold
                stegoImage.putpixel(pixelPos, pixelValue)
                log_file.write(f"inserted : {pixelValue}\t\tindex : {sdbIndex}\n")
                sdbIndex += 1
            elif hold > 3 and sdb[sdbIndex] == '0':
                log_file.write(f"pixVal before : {pixelValue}\t\t ")
                pixelValue = pixelValue - 4
                pixelValue = pixelValue + 3
                stegoImage.putpixel(pixelPos, pixelValue)
                sdb0posList.append(pixelPos)
                log_file.write(f"inserted : {pixelValue}\t\tindex : {sdbIndex}\n")
                sdbIndex += 1
            else:
                continue
        elif pixelValue >= t1 and pixelValue < t2:
            # Get the hold value
            hold = pixelValue & 0b00000011
            if hold <= 1 and sdb[sdbIndex] == '0':
                log_file.write(f"pixVal before : {pixelValue}\t\t ")
                pixelValue = pixelValue | hold
                stegoImage.putpixel(pixelPos, pixelValue)
                sdb0posList.append(pixelPos)
                log_file.write(f"inserted : {pixelValue}\t\tindex : {sdbIndex}\n")
                sdbIndex += 1
            elif hold <= 1 and sdb[sdbIndex] == '1':
                log_file.write(f"pixVal before : {pixelValue}\t\t ")
                pixelValue = pixelValue | 0b00000011
                pixelValue = pixelValue - 1
                stegoImage.putpixel(pixelPos, pixelValue)
                log_file.write(f"inserted : {pixelValue}\t\tindex : {sdbIndex}\n")
                sdbIndex += 1
            elif hold > 1 and sdb[sdbIndex] == '0':
                log_file.write(f"pixVal before : {pixelValue}\t\t ")
                pixelValue = pixelValue - 2
                pixelValue = pixelValue + 1
                stegoImage.putpixel(pixelPos, pixelValue)
                sdb0posList.append(pixelPos)
                log_file.write(f"inserted : {pixelValue}\t\tindex : {sdbIndex}\n")
                sdbIndex += 1
            elif hold > 1 and sdb[sdbIndex] == '1':
                log_file.write(f"pixVal before : {pixelValue}\t\t ")
                pixelValue = pixelValue | hold
                log_file.write(f"inserted : {pixelValue}\t\tindex : {sdbIndex}\n")
                sdbIndex += 1
            else:
                continue
        else:
            log_file.write(f"pixVal before : {pixelValue}\t\t ")
            pixelValue = pixelValue & 0b11111110
            pixelValue = pixelValue | int(sdb[sdbIndex])
            if pixelValue >= t1 and pixelValue <= t2:
                sdb0posList.append(pixelPos)
            stegoImage.putpixel(pixelPos, pixelValue)
            log_file.write(f"inserted : {pixelValue}\t\tindex : {sdbIndex}\n")
            sdbIndex += 1

    #save position of 0 embedded pixels
    if(sdb0pos(sdb0posList, sdb0pos_path)):
        print("position of 0 embedded pixels saved successfully")
    else:
        print("Error saving position of 0 embedded pixels")
    #save stego image
    stegoImage.save(stegoImagePath)
    print("Stego image saved successfully")
    return True

def countMSE(stegoImagePath, coverImagePath):
    #open stego image
    stegoImage = Image.open(stegoImagePath).convert("L")
    #open cover image
    coverImage = Image.open(coverImagePath).convert("L")
    #get image size
    width, height = stegoImage.size
    #initialize MSE
    MSE = 0
    #calculate MSE
    for x in range(width):
        for y in range(height):
            stegoPixel = stegoImage.getpixel((x, y))
            coverPixel = coverImage.getpixel((x, y))
            MSE += (stegoPixel - coverPixel) ** 2
    MSE = MSE / (width * height)
    return MSE

def countPSNR(stegoImagePath, coverImagePath):
    #get MSE
    MSE = countMSE(stegoImagePath, coverImagePath)
    #calculate PSNR
    PSNR = 10 * math.log10((255 ** 2) / MSE)
    return PSNR

def countSSIM(stegoImagePath, coverImagePath):
    # Open images
    coverImage = Image.open(coverImagePath).convert("L")
    stegoImage = Image.open(stegoImagePath).convert("L")
    
    # Convert images to NumPy arrays
    coverImageArray = np.array(coverImage)
    stegoImageArray = np.array(stegoImage)
    
    # Calculate SSIM
    SSIM = ssim(coverImageArray, stegoImageArray)
    return SSIM


data_path = "data/data.txt"
image_path = "img/cvr/axial2.bmp"
stego_image_path = "img/stg/axial2_stg.bmp"
sdb0pos_path = "data/sdb0pos.txt"

#threshold
t1 = 86
t2 = 171

# Get random pixel positions
pixel_positions = get_unique_random_pixel_positions(image_path, len(secret_data_bits(data_path)))
secret_key = create_secret_key(pixel_positions)

f = open("data/secret_key.txt", "w")
f.write(secret_key)
f.close()
# Embed secret datas
with open("data/log_embed.txt", "w") as log_file:
    embedding_algorithm(image_path, data_path, pixel_positions, t1, t2, stego_image_path, sdb0pos_path, log_file)

print("MSE: ", countMSE(stego_image_path, image_path))
print("PSNR: ", countPSNR(stego_image_path, image_path))
print("SSIM: ", countSSIM(stego_image_path, image_path))