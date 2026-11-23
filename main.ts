import { copyFile } from 'node:fs/promises';
import { resolve } from 'node:path';

const filename = 'entry.png';
// The grader can start in a different directory from the bundled image.
const source = resolve(import.meta.dirname, filename);
const outputDirectory = process.env.MAKEFUN_OUTPUT_DIR ?? '/output';

await copyFile(source, resolve(outputDirectory, filename));
