from dataclasses import dataclass
from PIL import Image


type Operation = rotate | combine

@dataclass
class rotate():
    image : Image.Image


@dataclass
class combine():
    image1 : Image.Image
    image2 : Image.Image

type Literal = Name


@dataclass
class Name():
    name : str
    def __str__(self):
        return self.name


def run():
    file_name = Name("Image/image1.jpg")
    print("literal: ", file_name)

    try:
        raster = Image.open(file_name.name)
        print("raster: ", raster)

        rotated_image = rotate(image = raster)
        rotated_image = raster.rotate(90)
        rotated_image.show()

    except:
        print("Error: Unable to find file")
        return


    


if __name__ == "__main__":
    run()
# Here is the link to the Pillow https://pillow.readthedocs.io/en/stable/handbook/tutorial.html
'''
The purpose of this project is to create a simple image manipulation language. While 
using the Pillow library. We will create AST node definitions and then create a run 
method
'''