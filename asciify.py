from PIL import Image, ImageDraw, ImageFont
from imageio import imread
import numpy as np
import string
import os
import imageio

class AsciiArt():
    
    charlist = string.printable[:-5] # all printable characters without \t \n \r \x0b \x0c
    
    def __init__(self, font='FreeMono', font_size=20, resizer=90):
        """
        font: One of the Pillow fonts, check list of available fonts in Pillow/Tests/fonts/
        font_size: Height (in pixels) of the ascii characters. Width is font_size*6/10. 
        resizer: Output image height will be font_size*6*resizer/10
        """
        self.font_size = font_size
        self.font = ImageFont.truetype('Pillow/Tests/fonts/'+font+'.ttf', self.font_size)
        self.font_image_size = (self.font_size*6/10, self.font_size) # practical rule of thumb
        self.resizer = resizer
        self.dataset_path = os.path.join(os.getcwd(), 'letterset')
        self.make_font_images()
        self.filters = self.load_font_images()
        
    def make_font_images(self):
        if os.path.exists(self.dataset_path):
            print('letterset/ already exists')
        else:
            print('Building letterset/')
            os.makedirs(self.dataset_path)
        for idx, ch in enumerate(self.charlist):
            image = Image.new(mode="L", size=self.font_image_size, color=(0))
            draw = ImageDraw.Draw(image)
            position = (0,0)
            draw.text(position, ch, (255), font=self.font)
            file_name = str(idx) + '.jpg' #'_' + font 
            file_name = os.path.join(self.dataset_path, file_name)
            image.save(file_name)
            
    def load_font_images(self):
        print('loading filters')
        filters = []
        normalized_filters =  []
        for each in os.listdir(self.dataset_path):
            image_data= np.array(Image.open('letterset/'+each).convert('L'), dtype=np.float32)
            filters.append(image_data)
        return filters
    
    def compare(self, subimage):
        best_dist = np.infty
        best_filt = np.zeros_like(subimage)
        for idx, filt in enumerate(self.filters):
            tmp = np.linalg.norm(subimage-filt)
            if tmp < best_dist:
                best_dist = tmp
                best_filt = self.filters[idx]
        return best_filt
    
    def asciify(self, filename=''):
        img_br = Image.open(filename).convert('L')
        width, height = img_br.size
        r = float(height)/width
        wn = int(self.font_image_size[0]*self.resizer)
        hn = int(r*wn)
        img = np.array(img_br.resize((wn,hn)))
        
        new_img = np.zeros_like(img, dtype=np.uint8)
        for n in np.linspace(start=0,
                             stop=hn,
                             num=hn//self.font_image_size[1],
                             endpoint=True,
                             dtype=np.int32)[:-1]:
            for m in np.linspace(start=0,
                                 stop=wn,
                                 num=wn//self.font_image_size[0],
                                 endpoint=True,
                                 dtype=np.int32)[:-1]:
                subimage = img[n:n+self.font_image_size[1],m:m+self.font_image_size[0]]
                filt = self.compare(subimage)
                new_img[n:n+self.font_image_size[1],m:m+self.font_image_size[0]] = filt
        return Image.fromarray(new_img)