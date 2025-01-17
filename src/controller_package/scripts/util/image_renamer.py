# adapted from https://blog.alexgordienko.com/renaming-photos-in-bulk-with-python/ 

import os

# Function to rename multiple photos
def main():
    # ask user for some info about photos on run.
    image_dir = input("/home/fizzer/data/images/")
    directory = str(f"/home/fizzer/data/images/{image_dir}")

    i = 0
    dirs = os.listdir(directory)
    dirs.sort()
    print(dirs)
    for filename in dirs:
        print(f"current file name: {filename}")
        label = input("label: ")
        new_name =  f"/home/fizzer/data/labelled/{label}.png"
        old_name = directory + "/" + filename

        print(f"new name: {new_name}")
        os.rename(old_name, new_name)
        i += 1
    print("Done!")

if __name__ == '__main__':
    main()