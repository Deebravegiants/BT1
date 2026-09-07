# [M] ExifReader is vulnerable to denial of service via unbounded decompression of image metadata

## Summary
Severity: Medium
Advisory: GHSA-rr89-w3h9-m66j
CVE: CVE-2026-8814
CWE: CWE-409
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2026-05-29
Source: https://github.com/advisories/GHSA-rr89-w3h9-m66j
Type: github-advisory

## Affected
- npm: `exifreader` — affected >=4.20.0 <4.39.0

## Details
### Impact

Versions of ExifReader from 4.20.0 through 4.38.1 do not bound the size of decompressed metadata blocks. When a caller invokes the asynchronous API (e.g. `ExifReader.load(file)` or `ExifReader.load(buffer, {async: true})`) on an attacker-supplied image, a small compressed chunk in the file can expand to hundreds of megabytes of memory, consuming heap and CPU until the process slows down or runs out of memory.

The affected paths share a single decompression utility, so the issue is reachable through any compressed metadata block the library handles asynchronously, including:

- PNG `zTXt`, compressed `iTXt`, and `iCCP` chunks (deflate)
- JPEG XL Brotli-compressed Exif and XMP blocks

A typical proof of concept produced roughly 1000× expansion (for example, ~32 KB of compressed input expanded to ~32 MB of output, ~130 KB to ~128 MB).

Both the npm package and the `dist/` bundle published from this repository (consumed by Bower and other users of the prebuilt artifact) are affected.

### Patches

Fixed in **4.39.0**. The decompression utility now reads the decompressed stream incrementally and aborts as soon as the running total would exceed a configurable limit. The default cap is **128 MiB** per metadata block, which is well above any realistic legitimate value. When a block exceeds the cap, that block is skipped (a warning is emitted via `console.warn`) and the remaining tags are returned as usual.

The cap is configurable via the new `maxDecompressedSize` field on the `decompress` option, in bytes:

```javascript
const tags = await ExifReader.load(file, {
    async: true,
    decompress: {
        maxDecompressedSize: 16 * 1024 * 1024 // 16 MiB
    }
});
```

The same cap applies to results returned by user-supplied custom `brotli`/`deflate` functions.

### Workarounds

- If upgrading is not possible, avoid invoking the asynchronous API on untrusted inputs. The synchronous code path skips compressed metadata blocks entirely and is not affected. Alternatively, pre-validate input files by source or size before passing them to ExifReader.

### Resources

- Patch: https://github.com/mattiasw/ExifReader/commit/5f116128adc19f674902f8bf582bfe7dd0a36375
- README — "Limiting decompressed metadata size": https://github.com/mattiasw/ExifReader/blob/main/README.md#limiting-decompressed-metadata-size

## References
- https://github.com/mattiasw/ExifReader/security/advisories/GHSA-rr89-w3h9-m66j
- https://nvd.nist.gov/vuln/detail/CVE-2026-8814
- https://github.com/mattiasw/ExifReader/commit/5f116128adc19f674902f8bf582bfe7dd0a36375
- https://github.com/mattiasw/ExifReader
- https://security.snyk.io/vuln/SNYK-JS-EXIFREADER-16689340
