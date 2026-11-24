[![make.fun · news-image-20261123](https://make.fun/badge/news-image-20261123.svg)](https://make.fun/bounty/news-image-20261123?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261123)
[![rank](https://make.fun/badge/news-image-20261123/2440749975/news-image-20261123/rank.svg)](https://make.fun/bounty/news-image-20261123/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261123)
[![reward](https://make.fun/badge/news-image-20261123/2440749975/news-image-20261123/reward.svg)](https://make.fun/bounty/news-image-20261123?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261123)

# The World Today
A code-drawn front page for Tuesday, 24 November 2026: eight stories and a single-line market ticker.

Run `python3 draw.py` with Pillow 10.2 and the system DejaVu and Liberation TrueType fonts to regenerate `entry.png`. The renderer prints the measured width of every line and the total height of every block against its allotted space, in final-image pixels rounded up. It refuses to publish a line that does not fit.

Run `MAKEFUN_OUTPUT_DIR=out node main.ts` to publish the finished PNG. The Node 22 entry needs only its standard library and the bundled image; the default output directory is `/output`.
