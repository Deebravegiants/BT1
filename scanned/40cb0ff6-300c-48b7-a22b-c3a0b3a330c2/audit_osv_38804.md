# [M] ImageMagick: Heap Buffer Over-Read in IPTC encoder

## Summary
Severity: Medium
Advisory: CVE-2026-42326
Aliases: GHSA-7wff-wpr6-vmhm
CVSS: 5.1 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:L)
Published: 2026-06-10
Source: https://osv.dev/vulnerability/CVE-2026-42326
Type: osv

## Details
ImageMagick is free and open-source software used for editing and manipulating digital images. Prior to versions 6.9.13-47 and 7.1.2-22, when writing an IPTC output file a malicious input file could cause an out of bounds read of a single byte. This issue has been patched in versions 6.9.13-47 and 7.1.2-22.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/42xxx/CVE-2026-42326.json
- https://github.com/ImageMagick/ImageMagick/security/advisories/GHSA-7wff-wpr6-vmhm
- https://nvd.nist.gov/vuln/detail/CVE-2026-42326
