# [M] CVE-2025-48175

## Summary
Severity: Medium
Advisory: CVE-2025-48175
Aliases: GHSA-762c-2538-h844
CVSS: 4.5 (CVSS:3.1/AV:L/AC:H/PR:N/UI:N/S:C/C:N/I:L/A:L)
Published: 2025-05-16
Source: https://osv.dev/vulnerability/CVE-2025-48175
Type: osv

## Details
In libavif before 1.3.0, avifImageRGBToYUV in reformat.c has integer overflows in multiplications involving rgbRowBytes, yRowBytes, uRowBytes, and vRowBytes.

## References
- https://lists.debian.org/debian-lts-announce/2025/05/msg00031.html
- https://github.com/AOMediaCodec/libavif/security/advisories/GHSA-762c-2538-h844
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/48xxx/CVE-2025-48175.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-48175
- https://github.com/AOMediaCodec/libavif/commit/64d956ed5a602f78cebf29da023280944ee92efd
- https://github.com/AOMediaCodec/libavif/pull/2769
