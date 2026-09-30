# [H] libsixel: Integer overflow leads to Out-of-bounds Read in img2sixel

## Summary
Severity: High
Advisory: CVE-2026-33019
Aliases: GHSA-c854-ffg9-g72c
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:H)
Published: 2026-04-14
Source: https://osv.dev/vulnerability/CVE-2026-33019
Type: osv

## Details
libsixel is a SIXEL encoder/decoder implementation derived from kmiya's sixel. Versions 1.8.7 and prior contain an integer overflow leading to an out-of-bounds heap read in the --crop option handling of img2sixel, where positive coordinates up to INT_MAX are accepted without overflow-safe bounds checking. In sixel_encoder_do_clip(), the expression clip_w + clip_x overflows to a large negative value when clip_x is INT_MAX, causing the bounds guard to be skipped entirely, and the unclamped coordinate is passed through sixel_frame_clip() to clip(), which computes a source pointer far beyond the image buffer and passes it to memmove(). An attacker supplying a specially crafted crop argument with any valid image can trigger an out-of-bounds read in the heap, resulting in a reliable crash and potential information disclosure. This issue has been fixed in version 1.8.7-r1.

## References
- https://github.com/saitoha/libsixel/releases/tag/v1.8.7-r1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/33xxx/CVE-2026-33019.json
- https://github.com/saitoha/libsixel/security/advisories/GHSA-c854-ffg9-g72c
- https://nvd.nist.gov/vuln/detail/CVE-2026-33019
