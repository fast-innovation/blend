#!/usr/bin/env python3.6
# PYTHON_ARGCOMPLETE_OK
import sys
import os
import argparse
import argcomplete
import cv2
from collections import OrderedDict


def run(args):
    all_images = OrderedDict()

    path_base, images_base = None, None

    for folder in args.folder:
        path = os.path.join(folder, "./Output")

        all_images[path] = []
        ids = []

        for file_path in os.listdir(path):
            file_path = os.path.join(path, file_path)

            if os.path.isfile(file_path) and file_path.endswith(".jpg"):
                index, ext = os.path.splitext(os.path.basename(file_path))
                ids.append(int(index))
                all_images[path].append(file_path)

        if not len(all_images[path]):
            raise ValueError("image folder empty.")

        all_images[path].sort()
        ids.sort()

        if len(ids) - 1 != max(ids) - min(ids):
            raise ValueError(f"missing images: min={min(all_images[path])} max={max(all_images[path])} len={len(all_images[path])}")

        print(f"{folder}: {len(all_images[path])}")

        if path_base is None:
            path_base, images_base = all_images.popitem(last=False)
        else:
            if len(all_images[path]) != len(images_base):
                raise ValueError("image counts don't match.")

    if args.remove_output and os.path.exists(args.out):
        try:
            os.rmdir(args.out)
            os.unlink(args.out)
        except (OSError, IOError):
            pass

    if not os.path.exists(args.out):
        os.mkdir(args.out)
    else:
        raise ValueError("invalid output.")

    zipped = tuple(zip(*all_images.values()))

    for image_index, image_base_path in enumerate(images_base):
        print(f"processing image {image_index} .", end='')
        sys.stdout.flush()

        image = cv2.imread(image_base_path)

        image_blend_paths = zipped[image_index]

        for blend_path in image_blend_paths:
            image_blend = cv2.imread(blend_path)
            image = cv2.bitwise_or(image, image_blend)
            del image_blend
            print(".", end="")

        cv2.imwrite(os.path.join(args.out, f"{image_index:04}.jpg"), image)
        del image

        print("done.")


def main():
    parser = argparse.ArgumentParser(prog="blend")
    parser.add_argument('-rm', '--remove-output', action='store_true', default=False, help='clear output folder')
    parser.add_argument('folder', nargs='+', help='base folder to merge from')
    parser.add_argument('out', help='output folder')
    argcomplete.autocomplete(parser)
    args = parser.parse_args()

    try:
        run(args)

    except KeyboardInterrupt:
        exit("")


if __name__ == '__main__':
    main()
