import argparse
from functools import cache
from math import ceil
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


SCALE = 3
SIZE = 1024
PAPER = '#faf6ea'
INK = '#162322'
GREEN = '#11473e'
MINT = '#b5ddc3'
LIME = '#e0e991'
HAIRLINE = '#acb4a8'
FONTS = Path('/usr/share/fonts/truetype')
MAST = 'dejavu/DejaVuSerif-Bold'
LABEL = 'dejavu/DejaVuSans-Bold'
TITLE = 'liberation/LiberationSerif-Bold'
BODY = 'liberation/LiberationSans-Regular'
TAPE = 'liberation/LiberationSans-Bold'

LEAD = (
    'NVIDIA COMEBACK', 'Huang Is Back: Nvidia Soars 31% in Biggest Jump in 23 Years',
    "Nvidia's board reinstated co-founder Jensen Huang as CEO on Monday, just 11 days after he "
    'stepped down. Shares surged 31.48% to $165.05, adding about $1 trillion in market value in a single session.')
STORIES = (
    ('WALL STREET', 'Best Day Since April 2025 Snaps 7-Day Slide',
     'The S&P 500 jumped 4.73% to 7,237 and the Nasdaq Composite leapt 6.51% to 24,090, '
     'while the Dow gained 3.01% in a relief rally across AI and chip stocks.'),
    ('CHIP CRACKDOWN', 'US Blacklists Megaspeed Over Nvidia Smuggling Plot',
     'Washington put Singapore-based Megaspeed International and six other Southeast Asian firms '
     'on its Entity List, at the centre of an alleged scheme to divert advanced Nvidia chips.'),
    ('UKRAINE', 'Zelensky Urges Four-Way Talks With Russia, US, Europe',
     "Ukraine's president called for a meeting with Russia, the United States and European leaders "
     'as soon as possible, saying Kyiv is ready to meet as early as Tuesday.'),
    ('SANCTIONS', 'EU Proposes 22nd Sanctions Package on Russia',
     "The European Commission's new package targets banks and crypto platforms, and would bar "
     'Russian teams and athletes from competing under the Russian flag at EU events.'),
    ('CLIMATE', "'Worst COP Ever': Blame Game After Antalya Failure",
     'Pacific leaders accused big emitters of betrayal after COP31 in Türkiye collapsed without '
     'a deal, leaving small island states vowing to press ahead on their own.'),
    ('AIR DEFENSE', "Russian Jets Enter South Korea's Air Defense Zone",
     'Seoul said several Russian aircraft flew through its air defense identification zone over '
     'waters between Korea and Japan on Tuesday, without violating its airspace.'))
ALLIES = (
    'ALLIES', 'Pentagon Rebukes Canada Over Defence Spending and F-35 Review',
    'The Pentagon accused Ottawa of falling short as a partner in defending North America, '
    "citing defence shortfalls and Canada's rethink of US-made F-35 jets.")
TICKER = ('NVDA $165.05 +31.48%  |  S&P 500 7,237 +4.73%  |  NASDAQ 24,090 +6.51%  |  '
          'GOLD $3,656 +3.99%  |  OIL $79.98 -4.76%  |  BITCOIN $60,669 -0.81%')


def coords(values):
    return tuple(round(value * SCALE) for value in values)


@cache
def font(face, size):
    return ImageFont.truetype(str(FONTS / f'{face}.ttf'), round(size * SCALE))


class Plate:
    def __init__(self):
        self.image = Image.new('RGB', coords((SIZE, SIZE)), PAPER)
        self.draw = ImageDraw.Draw(self.image)
        self.proof = []

    def line(self, points, fill, weight=1):
        self.draw.line([coords(point) for point in points], fill, max(1, round(weight * SCALE)), joint='curve')

    def shape(self, points, fill):
        self.draw.polygon([coords(point) for point in points], fill)

    def rect(self, box, fill):
        self.draw.rectangle(coords(box), fill)

    def oval(self, box, fill=None, outline=None, weight=1):
        self.draw.ellipse(coords(box), fill, outline, max(1, round(weight * SCALE)))

    @cache
    def metrics(self, words, face):
        left, top, right, bottom = self.draw.textbbox((0, 0), words, font=face, anchor='ls')
        end = max(right, ceil(self.draw.textlength(words, font=face)))
        return min(0, left), top, end, bottom

    def width(self, words, face):
        left, _, right, _ = self.metrics(words, face)
        return right - left

    def wrap(self, text, face, width, break_before):
        if break_before:
            before, space, after = text.partition(' ' + break_before)
            preferred = (before, break_before + after)
            if space and all(self.width(line, face) <= width for line in preferred):
                return preferred
        words = text.split(' ')
        lines = [words[0]]
        for word in words[1:]:
            trial = lines[-1] + ' ' + word
            if self.width(trial, face) <= width:
                lines[-1] = trial
            else:
                lines.append(word)
        return lines

    def text(self, name, text, box, family, maximum, *, leading=1.07, mode='wrap', fill=INK,
             center=False, middle=False, break_before=None):
        left, top, width, height = coords(box)
        if min(left, top) < SCALE or max(left + width, top + height) > (SIZE - 1) * SCALE:
            raise ValueError(f'{name}: box outside page margins')
        for steps in range(round(maximum * SCALE), 10 * SCALE - 1, -1):
            face = font(family, steps / SCALE)
            lines = [text] if mode == 'single' else self.wrap(text, face, width, break_before)
            metrics = [self.metrics(line, face) for line in lines]
            stride = round(steps * leading)
            bounds = [(index * stride + up, index * stride + down)
                      for index, (_, up, _, down) in enumerate(metrics)]
            high, low = min(up for up, _ in bounds), max(down for _, down in bounds)
            if (all(end - start <= width for start, _, end, _ in metrics) and low - high <= height
                    and all(first[1] < second[0] for first, second in zip(bounds, bounds[1:]))):
                break
        else:
            raise ValueError(f'{name}: no size fits {box}')
        if ' '.join(lines) != text:
            raise ValueError(f'{name}: copy changed during wrap')
        self.proof.append(f'[{name}] height {ceil((low - high) / SCALE)} / {box[3]} px')
        baseline = top - high + ((height - low + high) // 2 if middle else 0)
        for index, (line, (start, up, end, down)) in enumerate(zip(lines, metrics)):
            origin = left - start + ((width - end + start) // 2 if center else 0)
            base = baseline + index * stride
            if not (left <= origin + start <= origin + end <= left + width
                    and top <= base + up <= base + down <= top + height):
                raise ValueError(f'{name}: line outside box: {line}')
            self.draw.text((origin, base), line, font=face, fill=fill, anchor='ls')
            self.proof.append(f'{ceil((end - start) / SCALE):>4} / {box[2]:<4}  {line}')
        return max(ceil((end - start) / SCALE) for start, _, end, _ in metrics)


def chip(page):
    copper, shade, edge = '#72a98e', '#082e29', '#43806c'

    def project(across, back, lift):
        return (890 + across * 1.02 - back * .81, 243 + across * .42 + back * .64 - lift)

    def ring(radius, lift):
        return [project(across, back, lift) for across, back in
                ((-radius, -radius), (radius, -radius), (radius, radius), (-radius, radius))]

    def slab(radius, lift, depth, surface, front, side):
        rim, foot = ring(radius, lift), ring(radius, lift - depth)
        page.shape([rim[1], rim[2], foot[2], foot[1]], side)
        page.shape([rim[2], rim[3], foot[3], foot[2]], front)
        page.shape(rim, surface)
        page.line([*rim, rim[0]], MINT, 1)

    for row in range(18):
        for column in range(19):
            across, back = 785 + column * 12 + (row % 2) * 5, 150 + row * 11
            page.oval((across, back, across + 1, back + 1), edge)
    for offset in (-36, -12, 12, 36):
        for direction in (-1, 1):
            points = [project(offset, direction * 55, -23), project(offset, direction * 64, -23),
                      project(offset - 6, direction * 70, -23), project(offset - 6, direction * 78, -23)]
            page.line(points, copper, 1)
            across, back = points[-1]
            page.oval((across - 2, back - 2, across + 2, back + 2), GREEN, copper)
    slab(55, -18, 5, '#50856e', shade, '#284f45')
    for offset in range(-43, 44, 7):
        for direction in (-1, 1):
            for transpose in (False, True):
                points = [(offset, direction * reach, lift) for reach, lift in ((43, 8), (50, 6), (50, -8), (54, -11))]
                page.line([project(back, across, lift) if transpose else project(across, back, lift)
                           for across, back, lift in points], MINT, 2.3)
    slab(45, 13, 10, '#8eb49a', '#234c40', '#426b52')
    for offset in range(-39, 44, 4):
        page.line([project(offset, 45, 12), project(offset - 2, 45, 5)], copper, 1)
    slab(34, 18, 5, '#204e40', shade, '#376350')
    rim = ring(29, 18)
    page.line([*rim, rim[0]], '#82a88a', .8)
    for stripe in range(-24, 25, 6):
        page.line([project(stripe, -25, 18), project(stripe, 25, 18)], edge, .7)
    arrow = [(831, 231), (854, 199), (871, 210), (900, 169), (889, 162),
             (927, 155), (931, 193), (919, 184), (876, 240), (859, 225), (843, 245)]
    page.shape([(across + 4, down + 8) for across, down in arrow], shade)
    page.shape(arrow, LIME)
    page.line([(843, 239), (858, 218), (875, 231), (915, 177)], '#79905e', 1.4)
    for offset in range(0, 12, 3):
        page.line([(896 + offset, 166), (898 + offset, 163)], '#79905e', .8)


def vignette(page, name, left, top, size, color):
    def point(across, down):
        return (left + across * size / 32, top + down * size / 32)

    def stroke(points, weight=1.7, tint=color):
        page.line([point(*position) for position in points], tint, weight * size / 32)

    def shape(points, tint=color):
        page.shape([point(*position) for position in points], tint)

    def oval(box, solid=False):
        page.oval((*point(*box[:2]), *point(*box[2:])), color if solid else None, color, size / 20)

    if name == 'WALL STREET':
        for start, level in ((3, 21), (10, 17), (17, 19), (24, 11)):
            shape([(start, 28), (start, level), (start + 4, level - 1), (start + 4, 28)])
        stroke([(2, 16), (11, 9), (17, 12), (28, 3)], 2.2)
        stroke([(22, 3), (29, 2), (28, 8)], 2)
    elif name == 'CHIP CRACKDOWN':
        shape([(6, 7), (25, 6), (26, 25), (7, 26)])
        stroke([(10, 11), (21, 10), (22, 21), (11, 22), (10, 11)], 1.3, PAPER)
        for offset in (9, 14, 19, 24):
            stroke([(offset, 3), (offset, 7)])
            stroke([(offset, 26), (offset, 30)])
            stroke([(2, offset), (7, offset)])
            stroke([(25, offset), (30, offset)])
    elif name == 'UKRAINE':
        shape([(16, 2), (28, 6), (27, 17), (23, 24), (16, 30), (8, 24), (4, 17), (3, 6)])
        stroke([(7, 9), (16, 5), (24, 8), (23, 17), (20, 22), (16, 25), (11, 21), (8, 16)], 1.3, PAPER)
        stroke([(12, 11), (12, 15), (16, 18), (20, 15), (20, 11)], 1.4, PAPER)
        stroke([(16, 9), (16, 21)], 1.5, PAPER)
    elif name == 'SANCTIONS':
        shape([(2, 10), (16, 2), (30, 10), (29, 12), (3, 12)])
        stroke([(7, 9), (16, 5), (24, 9)], 1, PAPER)
        for offset in (6, 12, 18, 24):
            stroke([(offset, 14), (offset, 24)], 2.8)
        stroke([(3, 26), (29, 26)], 2)
        stroke([(1, 29), (31, 29)], 1.5)
    elif name == 'CLIMATE':
        oval((10, 2, 21, 13), True)
        for level in (15, 21, 27):
            stroke([(2, level), (6, level + 1), (11, level - 1), (16, level - 2),
                    (22, level + 1), (27, level + 1), (31, level - 1)], 1.8)
    elif name == 'AIR DEFENSE':
        shape([(2, 26), (12, 15), (7, 6), (10, 5), (18, 10), (26, 4), (31, 3),
               (28, 9), (21, 16), (24, 25), (22, 27), (15, 20), (5, 28)])
        stroke([(9, 22), (25, 9)], 1, PAPER)
        stroke([(2, 17), (7, 12)], 1.2)
        stroke([(11, 29), (15, 25)], 1.2)
    elif name == 'ALLIES':
        shape([(16, 1), (19, 7), (22, 5), (21, 15), (25, 10), (26, 13), (31, 12),
               (29, 18), (31, 19), (23, 24), (24, 26), (17, 25), (17, 31), (15, 31),
               (15, 25), (8, 26), (9, 23), (1, 19), (3, 17), (1, 12), (6, 13),
               (7, 10), (12, 15), (10, 5), (13, 7)])
        stroke([(16, 5), (16, 25)], .65, PAPER)
        for across, down in ((5, 16), (10, 15), (12, 9), (27, 15), (22, 15), (20, 9)):
            stroke([(across, down), (16, 23 if down >= 15 else 17)], .5, PAPER)


def render(destination):
    page = Plate()
    page.rect((32, 9, 992, 14), INK)
    page.text('Masthead', 'THE WORLD TODAY', (31, 19, 962, 63), MAST, 83, mode='single', center=True)
    page.text('Date', 'Tuesday, 24 November 2026', (293, 87, 438, 26), LABEL, 26,
              mode='single', center=True, middle=True)
    for start, end in ((32, 285), (739, 992)):
        page.line([(start, 99), (end, 99)], INK, 1.4)
        page.line([(start, 103), (end, 103)], HAIRLINE, .7)

    page.rect((0, 123, SIZE, 359), GREEN)
    page.rect((32, 139, 235, 163), MINT)
    page.text('Lead kicker', LEAD[0], (40, 141, 187, 20), LABEL, 17, mode='single',
              center=True, middle=True, fill=GREEN)
    page.line([(248, 151), (760, 151)], '#528272', .8)
    page.text('Lead headline', LEAD[1], (32, 173, 738, 96), TITLE, 50, leading=.98, fill=PAPER)
    page.text('Lead summary', LEAD[2], (34, 281, 733, 65), BODY, 19.5, leading=1.13, fill=PAPER)
    chip(page)

    colors = ('#1e6353', '#8a4c28', '#235b7a', '#77432e', '#316851', '#375a78')
    breaks = ('Snaps', 'Over', 'With', 'Sanctions', 'After', 'South')
    page.line([(512, 374), (512, 860)], HAIRLINE, .8)
    for index, ((name, title, body), color) in enumerate(zip(STORIES, colors)):
        left, top = (32, 532)[index % 2], 361 + 170 * (index // 2)
        vignette(page, name, left, top + 9, 26, color)
        span = page.text(f'{name} kicker', name, (left + 35, top + 14, 225, 15), LABEL, 15,
                         mode='single', middle=True, fill=color)
        page.line([(left + 47 + span, top + 22), (left + 460, top + 22)], HAIRLINE, .7)
        page.text(f'{name} headline', title, (left, top + 37, 460, 53), TITLE, 28,
                  leading=1.02, break_before=breaks[index])
        page.text(f'{name} summary', body, (left + 1, top + 96, 459, 67), BODY, 17.3, leading=1.13)
        if index in (1, 3):
            page.line([(32, top + 170), (992, top + 170)], INK, 1.2)

    page.rect((0, 872, SIZE, 984), '#efecde')
    page.line([(32, 872), (992, 872)], INK, 2)
    page.line([(32, 876), (992, 876)], HAIRLINE, .8)
    vignette(page, 'ALLIES', 44, 897, 62, '#93482f')
    page.line([(121, 889), (121, 968)], HAIRLINE, .8)
    page.text('ALLIES kicker', ALLIES[0], (139, 887, 100, 15), LABEL, 15, mode='single', fill='#93482f')
    page.text('ALLIES headline', ALLIES[1], (138, 908, 854, 28), TITLE, 28, mode='single')
    page.text('ALLIES summary', ALLIES[2], (139, 943, 853, 35), BODY, 17, leading=1.13, break_before='citing')

    page.rect((0, 984, SIZE, SIZE), INK)
    page.line([(32, 988), (992, 988)], '#4e6c5f', .8)
    page.text('Ticker', TICKER, (30, 994, 964, 23), TAPE, 14, mode='single', center=True, middle=True, fill=PAPER)
    page.image.resize((SIZE, SIZE), Image.Resampling.LANCZOS).save(
        destination, format='PNG', optimize=False, compress_level=9)
    print('Print proof in output pixels, rounded up. Lines: measured width / box width.')
    print('\n'.join(page.proof))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Draw the 24 November 2026 front page and print its fit proof.')
    parser.add_argument('output', nargs='?', type=Path, default=Path(__file__).with_name('entry.png'))
    render(parser.parse_args().output)
