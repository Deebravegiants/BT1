# [M] In libavif before 1.3.0, avifImageRGBToYUV in reformat.c has integer overflows in multiplications...

## Summary
Severity: Medium
Advisory: JLSEC-2026-126
Ecosystem: Julia
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:L)
Published: 2026-04-17
Source: https://osv.dev/vulnerability/JLSEC-2026-126
Type: osv

## Affected
- Julia: `libavif_jll` — affected >=0 <1.3.0+0

## Details
In libavif before 1.3.0, avifImageRGBToYUV in reformat.c has integer overflows in multiplications involving rgbRowBytes, yRowBytes, uRowBytes, and vRowBytes.

## References
- https://github.com/AOMediaCodec/libavif/commit/64d956ed5a602f78cebf29da023280944ee92efd
- https://github.com/AOMediaCodec/libavif/pull/2769
- https://github.com/AOMediaCodec/libavif/security/advisories/GHSA-762c-2538-h844
- https://github.com/advisories/GHSA-44mp-2g68-7wvv
- https://lists.debian.org/debian-lts-announce/2025/05/msg00031.html
- https://nvd.nist.gov/vuln/detail/CVE-2025-48175
