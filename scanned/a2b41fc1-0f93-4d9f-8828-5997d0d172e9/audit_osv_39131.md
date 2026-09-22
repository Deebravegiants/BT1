# [M] OpenImageIO: Integer wraparound in bounds check of decode_pixel leads to out-of-bounds read in TGA paletted image decoder

## Summary
Severity: Medium
Advisory: CVE-2026-43996
Aliases: GHSA-mq8j-73c4-cr55
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2026-05-14
Source: https://osv.dev/vulnerability/CVE-2026-43996
Type: osv

## Details
OpenImageIO is a toolset for reading, writing, and manipulating image files of any image file format relevant to VFX / animation. Prior to 3.0.18.0 and 3.1.13.0, the bounds check in TGAInput::decode_pixel computes k + palbytespp as unsigned 32-bit arithmetic. When k = 0xFFFFFFFC and palbytespp = 4, the addition wraps to 0, which compares less than palette_alloc_size and passes the check. The subsequent palette access uses the unwrapped k (0xFFFFFFFC) as the index, reading ~4 GB past the start of the palette buffer — SEGV. This vulnerability is fixed in 3.0.18.0 and 3.1.13.0.

## References
- https://github.com/AcademySoftwareFoundation/OpenImageIO/security/advisories/GHSA-mq8j-73c4-cr55
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/43xxx/CVE-2026-43996.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-43996
