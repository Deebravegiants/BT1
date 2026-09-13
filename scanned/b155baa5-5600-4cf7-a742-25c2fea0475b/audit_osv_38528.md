# [C] SAIL has heap buffer overflow in XWD decoder — bits_per_pixel vs pixmap_depth type confusion in byte-swap

## Summary
Severity: Critical
Advisory: CVE-2026-40492
Aliases: GHSA-526v-vm72-4v64
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-04-18
Source: https://osv.dev/vulnerability/CVE-2026-40492
Type: osv

## Details
SAIL is a cross-platform library for loading and saving images with support for animation, metadata, and ICC profiles. Prior to commit 36aa5c7ec8a2bb35f6fb867a1177a6f141156b02, the XWD codec resolves pixel format based on `pixmap_depth` but the byte-swap code uses `bits_per_pixel` independently. When `pixmap_depth=8` (BPP8_INDEXED, 1 byte/pixel buffer) but `bits_per_pixel=32`, the byte-swap loop accesses memory as `uint32_t*`, reading/writing 4x the allocated buffer size. This is a different vulnerability from the previously reported GHSA-3g38-x2pj-mv55 (CVE-2026-27168), which addressed `bytes_per_line` validation. Commit 36aa5c7ec8a2bb35f6fb867a1177a6f141156b02 contains a patch.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/40xxx/CVE-2026-40492.json
- https://github.com/HappySeaFox/sail/security/advisories/GHSA-526v-vm72-4v64
- https://nvd.nist.gov/vuln/detail/CVE-2026-40492
- https://github.com/HappySeaFox/sail/commit/36aa5c7ec8a2bb35f6fb867a1177a6f141156b02
