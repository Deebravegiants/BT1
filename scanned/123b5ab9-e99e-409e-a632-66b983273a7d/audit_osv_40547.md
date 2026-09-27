# [M] ImageMagick: Information Disclosure in MNG decoder because allocated memory is left unchanged

## Summary
Severity: Medium
Advisory: CVE-2026-53467
Aliases: GHSA-8g53-9m3c-69xg
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2026-07-01
Source: https://osv.dev/vulnerability/CVE-2026-53467
Type: osv

## Details
ImageMagick is free and open-source software used for editing and manipulating digital images. Prior to versions 6.9.13-51 and 7.1.2-26, the MNG decoder contains a possible heap information disclosure vulnerability because part of the pixels are left unchanged. This issue has been fixed in versions 6.9.13-51 and 7.1.2-26.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53467.json
- https://github.com/ImageMagick/ImageMagick/security/advisories/GHSA-8g53-9m3c-69xg
- https://nvd.nist.gov/vuln/detail/CVE-2026-53467
