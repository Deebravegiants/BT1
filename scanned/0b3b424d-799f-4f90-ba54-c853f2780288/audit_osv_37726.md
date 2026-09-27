# [H] libsixel: Integer Overflow in write_png_to_file() leads to Heap-based Buffer Overflow

## Summary
Severity: High
Advisory: CVE-2026-33020
Aliases: GHSA-2xgm-4x47-2x2p
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:H)
Published: 2026-04-14
Source: https://osv.dev/vulnerability/CVE-2026-33020
Type: osv

## Details
libsixel is a SIXEL encoder/decoder implementation derived from kmiya's sixel. Versions 1.8.7 and prior contain an integer overflow which leads to a heap buffer overflow via sixel_frame_convert_to_rgb888() in frame.c, where allocation size and pointer offset computations for palettised images (PAL1, PAL2, PAL4) are performed using int arithmetic before casting to size_t. For images whose pixel count exceeds INT_MAX / 4, the overflow produces an undersized heap allocation for the conversion buffer and a negative pointer offset for the normalization sub-buffer, after which sixel_helper_normalize_pixelformat() writes the full image data starting from the invalid pointer, causing massive heap corruption confirmed by ASAN. An attacker providing a specially crafted large palettised PNG can corrupt the heap of the victim process, resulting in a reliable crash and potential arbitrary code execution.
This issue has been fixed in version 1.8.7-r1.

## References
- https://github.com/saitoha/libsixel/releases/tag/v1.8.7-r1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/33xxx/CVE-2026-33020.json
- https://github.com/saitoha/libsixel/security/advisories/GHSA-2xgm-4x47-2x2p
- https://nvd.nist.gov/vuln/detail/CVE-2026-33020
