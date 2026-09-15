# [M] ImageMagick: Null Pointer Dereference in distort operation when passing incorrect arguments

## Summary
Severity: Medium
Advisory: CVE-2026-53463
Aliases: GHSA-p9rq-q46c-g4x6
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:L)
Published: 2026-06-10
Source: https://osv.dev/vulnerability/CVE-2026-53463
Type: osv

## Details
ImageMagick is free and open-source software used for editing and manipulating digital images. Prior to versions 6.9.13-50 and 7.1.2-25, when passing incorrect arguments in the distort operation a null pointer deference will occur. This issue has been patched in versions 6.9.13-50 and 7.1.2-25.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53463.json
- https://github.com/ImageMagick/ImageMagick/security/advisories/GHSA-p9rq-q46c-g4x6
- https://nvd.nist.gov/vuln/detail/CVE-2026-53463
