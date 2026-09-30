# [M] CImg Library: Integer overflow in PNM size check bypasses memory guard (_load_pnm)

## Summary
Severity: Medium
Advisory: CVE-2026-42144
Aliases: GHSA-4663-63fm-44gc
CVSS: 6.1 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:L/A:H)
Published: 2026-05-04
Source: https://osv.dev/vulnerability/CVE-2026-42144
Type: osv

## Details
CImg Library is a C++ library for image processing. Prior to commit 4ca26bc, there is an integer overflow vulnerability in the W*H*D size computation inside _load_pnm() that can bypass the memory allocation guard. A crafted PNM/PGM/PPM file with large dimension values causes the overflow to wrap around, allocating an undersized buffer and potentially triggering a heap buffer overflow. Any application using CImg to load untrusted image files is affected. This issue has been patched via commit 4ca26bc.

## References
- https://github.com/GreycLab/CImg/releases/tag/v.3.7.5
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/42xxx/CVE-2026-42144.json
- https://github.com/GreycLab/CImg/security/advisories/GHSA-4663-63fm-44gc
- https://nvd.nist.gov/vuln/detail/CVE-2026-42144
- https://github.com/GreycLab/CImg/issues/478
- https://github.com/GreycLab/CImg/commit/4ca26bce4d8c61fcd1507d5f9401b9fb1222c27d
