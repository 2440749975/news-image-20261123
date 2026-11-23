import argparse
from functools import cache
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


SCALE = 3
SIZE = 1024
PAPER = '#faf6ea'
INK = '#162322'
GREEN = '#11473e'
MINT = '#b5ddc3'
HAIRLINE = '#a9aaa0'
FONT_DIR = Path('/usr/share/fonts/truetype/dejavu')


def coords(values):
    return tuple(round(value * SCALE) for value in values)


class Plate:
    def __init__(self, image):
        self.image = image
        self.draw = ImageDraw.Draw(image)

    def line(self, points, fill, width=1):
        self.draw.line([coords(point) for point in points], fill, round(width * SCALE), joint='curve')

    def rect(self, box, fill):
        self.draw.rectangle(coords(box), fill)

    def oval(self, box, fill=None, outline=None, width=1):
        self.draw.ellipse(coords(box), fill, outline, round(width * SCALE))

    def shape(self, points, fill):
        self.draw.polygon([coords(point) for point in points], fill)

    def text(self, position, words, face, size, fill=INK, anchor='ls'):
        self.draw.text(coords(position), words, font=font(face, size), fill=fill, anchor=anchor)


@cache
def font(face, size):
    return ImageFont.truetype(str(FONT_DIR / f'DejaVu{face}.ttf'), size * SCALE)


def fitted(face, maximum, width, lines):
    return next(size for size in range(maximum, 0, -1)
                if all(font(face, size).getlength(line) <= width * SCALE for line in lines))


def treaty(page):
    sheet = Image.new('RGBA', coords((244, 239)))
    printwork = Plate(sheet)
    printwork.shape([(10, 7), (204, 7), (235, 38), (235, 231), (10, 231)], PAPER)
    printwork.shape([(204, 7), (235, 38), (204, 38)], '#92baa6')
    printwork.rect((27, 23, 65, 28), GREEN)
    printwork.rect((71, 23, 98, 28), '#92baa6')
    printwork.oval((47, 35, 197, 185), GREEN)
    for inset in (20, 49):
        printwork.oval((47 + inset, 35, 197 - inset, 185), outline='#689780', width=1.6)
    for top, bottom in ((66, 154), (85, 135)):
        printwork.oval((47, top, 197, bottom), outline='#689780', width=1.6)
    printwork.line([(48, 110), (196, 110)], '#689780', 1.6)
    printwork.line([(122, 36), (122, 184)], '#689780', 1.6)
    printwork.shape([(51, 89), (61, 69), (75, 54), (86, 52), (91, 60), (85, 68),
                     (88, 72), (79, 75), (76, 86), (67, 91), (69, 100), (75, 108),
                     (67, 106), (60, 96)], MINT)
    printwork.shape([(72, 112), (81, 110), (96, 118), (98, 125), (106, 130),
                     (99, 143), (94, 145), (90, 157), (83, 167), (81, 155),
                     (84, 143), (78, 135), (77, 123)], MINT)
    printwork.shape([(86, 51), (104, 40), (115, 40), (112, 48), (101, 58), (94, 60)], MINT)
    printwork.shape([(115, 96), (122, 87), (137, 86), (145, 91), (156, 91),
                     (161, 104), (168, 107), (162, 114), (156, 121), (154, 132),
                     (144, 147), (138, 148), (134, 136), (134, 125), (127, 115),
                     (119, 116), (111, 107)], MINT)
    printwork.shape([(122, 82), (124, 77), (130, 75), (132, 69), (139, 66),
                     (137, 62), (143, 51), (149, 47), (151, 53), (145, 65), (150, 66),
                     (157, 52), (167, 52), (183, 70), (189, 82), (193, 97), (184, 95),
                     (183, 105), (178, 112), (174, 101), (170, 98), (167, 101),
                     (160, 92), (153, 88), (150, 82), (141, 80), (143, 86),
                     (138, 83), (134, 79), (129, 84)], MINT)
    printwork.shape([(157, 133), (161, 127), (161, 135), (158, 140)], MINT)
    for baseline, end in ((201, 210), (211, 159)):
        printwork.line([(29, baseline), (end, baseline)], GREEN, 3)

    tear = [(129, 0), (124, 30), (131, 47), (113, 74), (122, 85), (107, 116),
            (117, 130), (102, 156), (107, 171), (93, 197), (99, 211), (88, 239)]
    for edge, offset, angle in ((0, (718, 189), 6), (244, (738, 201), -6)):
        mask = Image.new('L', sheet.size)
        Plate(mask).shape([(edge, 0), *tear, (edge, 239)], 255)
        half = Image.new('RGBA', sheet.size)
        half.paste(sheet, mask=mask)
        half = half.rotate(angle, Image.Resampling.BICUBIC, expand=True)
        page.image.paste(half, coords(offset), half)


def shield(icon, color):
    icon.shape([(34, 2), (57, 10), (54, 29), (48, 39), (34, 49), (20, 39),
                (14, 29), (11, 10)], color)
    icon.line([(34, 9), (49, 14), (47, 26), (43, 33), (34, 40), (25, 33),
               (21, 26), (19, 14), (34, 9)], PAPER, 2)
    icon.line([(34, 15), (34, 32)], PAPER, 2.5)
    icon.line([(28, 18), (28, 24), (34, 27), (40, 24), (40, 18)], PAPER, 2.5)


def chart(icon, color):
    for left, height in ((7, 22), (19, 16), (31, 19), (43, 10)):
        icon.rect((left, 45 - height, left + 7, 45), '#d9ccc2')
    icon.line([(5, 9), (21, 19), (31, 12), (57, 32)], color, 5)
    icon.shape([(46, 33), (61, 35), (60, 19)], color)
    icon.line([(4, 46), (63, 46)], color, 2)


def capitol(icon, color):
    icon.line([(34, 2), (34, 10)], color, 3)
    icon.shape([(34, 2), (44, 4), (34, 7)], color)
    icon.rect((30, 10, 38, 14), color)
    icon.oval((16, 13, 52, 48), color)
    icon.rect((9, 29, 59, 33), color)
    icon.rect((7, 34, 61, 48), PAPER)
    for left in (14, 24, 34, 44, 51):
        icon.rect((left, 35, left + 4, 44), color)
    icon.rect((7, 45, 61, 49), color)
    icon.line([(27, 27), (29, 20), (33, 16)], PAPER, 1.5)


def probe(icon, color):
    icon.oval((7, 8, 47, 48), color)
    for box in ((15, 18, 24, 26), (28, 30, 37, 38), (29, 14, 33, 18)):
        icon.oval(box, '#bdb4cb')
    icon.line([(42, 33), (49, 27), (52, 22)], color, 2)
    icon.line([(46, 18), (63, 6)], color, 2)
    icon.shape([(48, 12), (54, 8), (59, 15), (53, 19)], color)
    for left, top in ((41, 17), (58, 5)):
        icon.shape([(left, top), (left + 6, top - 4), (left + 10, top + 1),
                    (left + 4, top + 5)], color)


def brief(page, left, top, section, color, pictogram, headline, summary):
    page.text((left, top + 39), section, 'Sans-Bold', 26, color)
    label_end = font('Sans-Bold', 26).getlength(section) / SCALE
    page.line([(left + label_end + 15, top + 30), (left + 381, top + 30)], color, 1.4)
    tile = Image.new('RGBA', coords((69, 52)))
    pictogram(Plate(tile), color)
    page.image.paste(tile, coords((left + 387, top + 4)), tile)
    title_size = fitted('Sans-Bold', 40, 455, headline)
    body_size = fitted('Sans', 30, 455, summary)
    for index, words in enumerate(headline):
        page.text((left, top + 94 + index * 43), words, 'Sans-Bold', title_size)
    for index, words in enumerate(summary):
        page.text((left, top + 182 + index * 33), words, 'Sans', body_size)


def render(destination):
    page = Plate(Image.new('RGB', coords((SIZE, SIZE)), PAPER))
    page.rect((34, 15, 990, 21), INK)
    page.text((512, 102), 'THE WORLD TODAY', 'Serif-Bold', 83, anchor='ms')
    page.text((512, 150), 'Monday, 23 November 2026', 'Sans-Bold', 34, anchor='ms')
    for start, end in ((34, 223), (801, 990)):
        page.line([(start, 138), (end, 138)], INK, 2)

    page.rect((0, 171, 1024, 514), GREEN)
    page.rect((36, 194, 179, 233), MINT)
    page.text((107, 223), 'CLIMATE', 'Sans-Bold', 26, GREEN, 'ms')
    page.text((198, 223), 'Antalya, Türkiye', 'Sans-Bold', 27, PAPER)
    page.text((32, 319), 'COP31 collapses', 'Serif-Bold', 70, PAPER)
    page.text((32, 389), 'without a deal', 'Serif-Bold', 70, PAPER)
    page.text((36, 446), 'EU and about 130 other parties rejected', 'Sans', 31, PAPER)
    page.text((36, 484), 'text omitting a shift away from fossil fuels.', 'Sans', 31, PAPER)
    treaty(page)
    page.text((853, 484), 'Two days of overtime', 'Sans-Bold', 23, MINT, 'ms')

    page.line([(512, 534), (512, 982)], HAIRLINE, 1.6)
    page.line([(34, 756), (990, 756)], INK, 2)
    brief(page, 35, 525, 'UKRAINE', '#185789', shield,
          ('Russian strikes kill', 'at least 15 near Kyiv'),
          ('Sea drones hit a Russian', 'warship off Libya.'))
    brief(page, 534, 525, 'MARKETS', '#9a3a29', chart,
          ('AI bubble fears spark', 'global stock sell-off'),
          ('Nikkei −5.06%, S&P 500 −3.7%;', 'gold gains ~2.7% as a haven.'))
    brief(page, 35, 763, 'US POLITICS', '#8b4d15', capitol,
          ('Democrats win', '258+ House seats'),
          ('Their largest House majority', 'since 1992.'))
    brief(page, 534, 763, 'SPACE', '#61417b', probe,
          ('BepiColombo reaches', 'Mercury orbit'),
          ('Japanese-European probes', 'arrive after eight years.'))
    page.line([(34, 998), (990, 998)], INK, 1.5)
    page.rect((34, 1005, 990, 1010), INK)
    page.image.resize((SIZE, SIZE), Image.Resampling.LANCZOS).save(
        destination, format='PNG', optimize=False, compress_level=9)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Draw the 23 November 2026 front page.')
    parser.add_argument('output', nargs='?', type=Path, default=Path(__file__).with_name('entry.png'))
    render(parser.parse_args().output)
