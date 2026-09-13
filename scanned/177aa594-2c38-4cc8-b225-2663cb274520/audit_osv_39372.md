# [M] ImageMagick: Out-of-Bounds Read of a single byte in meta encoder

## Summary
Severity: Medium
Advisory: CVE-2026-45358
Aliases: GHSA-cr6r-hmj8-pr7r
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2026-06-10
Source: https://osv.dev/vulnerability/CVE-2026-45358
Type: osv

## Details
ImageMagick is free and open-source software used for editing and manipulating digital images. Prior to versions 6.9.13-47 and 7.1.2-22, an off by one in the meta encoder could result in an out of bounds read of a single byte in the meta encoder. This issue has been patched in versions 6.9.13-47 and 7.1.2-22.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/45xxx/CVE-2026-45358.json
- https://github.com/ImageMagick/ImageMagick/security/advisories/GHSA-cr6r-hmj8-pr7r
- https://nvd.nist.gov/vuln/detail/CVE-2026-45358
