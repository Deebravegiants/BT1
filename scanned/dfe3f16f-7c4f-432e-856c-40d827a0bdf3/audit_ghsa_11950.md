# [H] music-metadata has an infinite loop vulnerability in ASF parser

## Summary
Severity: High
Advisory: GHSA-v6c2-xwv6-8xf7
CVE: CVE-2026-32256
CWE: CWE-835
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-03-17
Source: https://github.com/advisories/GHSA-v6c2-xwv6-8xf7
Type: github-advisory

## Affected
- npm: `music-metadata` — affected >=0 <11.12.3

## Details
# Summary

music-metadata's ASF parser (`parseExtensionObject()` in `lib/asf/AsfParser.ts:112-158`) enters an infinite loop when a sub-object inside the ASF Header Extension Object has `objectSize = 0`.

## Root Cause

When objectSize is 0:
1. `remaining = 0 - 24 = -24`
2. `tokenizer.ignore(-24)` moves the read position backward by 24 bytes
3. `extensionSize -= 0` (loop counter never decreases)
4. `while (extensionSize > 0)` never exits
5. The same 24-byte header is re-read infinitely

This is the same pattern as CVE-2026-31808 (GHSA-5v7r-6r5c-r473) in file-type — strtok3's `AbstractTokenizer.ignore()` accepts negative values without validation.

## Affected Methods
- `parseFile()` — HANGS (FileTokenizer inherits vulnerable ignore())
- `parseBuffer()` — HANGS (BufferTokenizer inherits vulnerable ignore())
- `parseStream()` — NOT affected (ReadStreamTokenizer has own ignore() that throws RangeError)

## Impact
A 100-byte crafted .asf file permanently hangs any application using parseFile() or parseBuffer(). music-metadata has 2.2M weekly npm downloads.

## Suggested Fix
Validate `objectSize >= minimumHeaderSize` before calculating the payload. Or fix strtok3's `AbstractTokenizer.ignore()` to reject negative values.

## References
- https://github.com/Borewit/music-metadata/security/advisories/GHSA-v6c2-xwv6-8xf7
- https://nvd.nist.gov/vuln/detail/CVE-2026-32256
- https://github.com/Borewit/music-metadata
- https://github.com/Borewit/music-metadata/releases/tag/v11.12.3
