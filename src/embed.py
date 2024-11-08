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

#calculate secret data bits length (assuming the secret data is already in bits)
def length_sdb(secretDataPath):
    with open(secretDataPath, 'r') as secretDataFile:
        secretData = secretDataFile.read().strip() 
    return len(secretData) - len(secretData) % 8

#extract secret data bits from secret data file (assuming the secret data is already in bits)
def secret_data_bits(secretDataPath):
    with open(secretDataPath, 'r') as secretDataFile:
        secretData = secretDataFile.read().strip()
    # Remove white spaces and convert to a list of bits
    secretDataBits = list(secretData.replace(" ", ""))
    return secretDataBits

#check if host image capacity is less than or equal to SDB size
def check_capacity(coverImagePath, secretDataPath):
    coverImageCapacity = get_available_capacity(coverImagePath)
    secretDataBits = length_sdb(secretDataPath)
    return coverImageCapacity >= secretDataBits

#embed secret data into host image
def get_unique_random_pixel_positions(image_path, secret_key, sdb_length):
    # Buka host image
    image = Image.open(image_path).convert("L")
    width, height = image.size

    # Gunakan secret key sebagai seed untuk random number generator
    random.seed(secret_key)
    
    # Gunakan set untuk memastikan piksel yang dipilih tidak duplikat
    selected_pixels = set()
    
    # Pilih koordinat piksel secara acak dan pastikan tidak ada duplikasi
    while len(selected_pixels) < sdb_length:
        x = random.randint(0, width - 1)
        y = random.randint(0, height - 1)
        selected_pixels.add((x, y))
    
    # Kembalikan sebagai list jika diperlukan
    return list(selected_pixels)

def embedding_algorithm(coverImagePath, secretDataPath, pixelPosition,  t1, t2, stegoImagePath):
    #check if host image capacity is less than or equal to SDB size
    if not check_capacity(coverImagePath, secretDataPath):
        return False
    #embed secret data into host image
    stegoImage = Image.open(coverImagePath).convert("L")
    
    for pixelPos in pixelPosition:
        #get pixel value
        pixelValue = stegoImage.getpixel(pixelPos)
        print("Pixel value: ", pixelValue)
        #get secret data bit
        sdbIndex = 0
        sdb = secret_data_bits(secretDataPath)
        if pixelValue <= t1:
            # print("pixelValue <= t1")
            #get the hold value
            hold = pixelValue & 0b00000111
            # print("Hold: ", hold)
            if hold <= 3 and sdb[sdbIndex] == '0':
                print("Hold <= 3 and sdb[sdbIndex] == 0")
                print("Before: ", pixelValue)
                pixelValue = pixelValue or hold
                stegoImage.putpixel(pixelPos, pixelValue)
                sdbIndex += 1
                print("After:", stegoImage.getpixel(pixelPos))
            elif hold <= 3 and sdb[sdbIndex] == '1':
                print("Hold <= 3 and sdb[sdbIndex] == 1")
                print("Before: ", pixelValue)
                pixelValue = pixelValue or 0b00000111
                pixelValue = pixelValue - 3
                sdbIndex += 1
                print("After:", stegoImage.getpixel(pixelPos))
            elif hold > 3 and sdb[sdbIndex] == '1':
                print("Hold > 3 and sdb[sdbIndex] == 1")
                print("Before: ", pixelValue)
                pixelValue = pixelValue or hold
                stegoImage.putpixel(pixelPos, pixelValue)
                sdbIndex += 1
                print("After:", stegoImage.getpixel(pixelPos))
            elif hold > 3 and sdb[sdbIndex] == '0':
                print("Hold > 3 and sdb[sdbIndex] == 0")
                print("before: ", pixelValue)
                pixelValue = pixelValue - 4
                pixelValue = pixelValue + 3
                stegoImage.putpixel(pixelPos, pixelValue)
                sdbIndex += 1
            else:
                print("Else")
                continue
        elif pixelValue > t1 and pixelValue < t2:
            print("t1 < pixelValue < t2")
            #get the hold value
            hold = pixelValue & 0b00000011
            print("Hold: ", hold)
            if hold <= 1 and sdb[sdbIndex] == '0':
                print("Hold <= 1 and sdb[sdbIndex] == 0")
                print("Before: ", pixelValue)
                pixelValue = pixelValue or hold
                stegoImage.putpixel(pixelPos, pixelValue)
                sdbIndex += 1
                print("After: ", stegoImage.getpixel(pixelPos))
            elif hold <= 1 and sdb[sdbIndex] == '1':
                print("Hold <= 1 and sdb[sdbIndex] == 1")
                print("Before: ", pixelValue)
                pixelValue = pixelValue or 0b00000011
                pixelValue = pixelValue - 1
                stegoImage.putpixel(pixelPos, pixelValue)
                sdbIndex += 1
            elif hold > 1 and sdb[sdbIndex] == '0':
                print("Hold > 1 and sdb[sdbIndex] == 0")
                print("Before: ", pixelValue)
                pixelValue = pixelValue - 2
                pixelValue = pixelValue + 1
                stegoImage.putpixel(pixelPos, pixelValue)
                sdbIndex += 1
                print("After: ", stegoImage.getpixel(pixelPos))
            elif hold > 1 and sdb[sdbIndex] == '1':
                print("Hold > 1 and sdb[sdbIndex] == 1")
                print("Before: ", pixelValue)
                pixelValue = pixelValue or hold
                sdbIndex += 1
                print("After: ", stegoImage.getpixel(pixelPos))
            else:
                print("Else")
                continue

        else:
            print("pixelValue >= t2")
            print("Before: ", pixelValue)
            pixelValue = pixelValue & 0b11111110
            pixelValue = pixelValue | int(sdb[sdbIndex])
            stegoImage.putpixel(pixelPos, pixelValue)
            sdbIndex += 1
            print("After: ", stegoImage.getpixel(pixelPos))

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
secret_key = "my_secret_key_123"
image_path = "img/cvr/axial2.bmp"
stego_image_path = "img/stg/axial2_stg.bmp"

#threshold
t1 = 86
t2 = 171

# Get random pixel positions
pixel_positions = get_unique_random_pixel_positions(image_path, secret_key, length_sdb(data_path))

# Embed secret data
embedding_algorithm(image_path, data_path, pixel_positions, t1, t2, stego_image_path)
print("=====================================")
print("MSE: ", countMSE(stego_image_path, image_path))
print("PSNR: ", countPSNR(stego_image_path, image_path))
print("SSIM: ", countSSIM(stego_image_path, image_path))