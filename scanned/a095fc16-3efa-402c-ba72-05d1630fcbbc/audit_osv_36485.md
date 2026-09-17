# [H] Heap buffer overflow with attacker-controlled data in XBM parser

## Summary
Severity: High
Advisory: CVE-2026-23876
Aliases: GHSA-r49w-jqq3-3gx8
CVSS: 8.1 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-01-20
Source: https://osv.dev/vulnerability/CVE-2026-23876
Type: osv

## Details
ImageMagick is free and open-source software used for editing and manipulating digital images. Prior to versions 7.1.2-13 and 6.9.13-38, a heap buffer overflow vulnerability in the XBM image decoder (ReadXBMImage) allows an attacker to write controlled data past the allocated heap buffer when processing a maliciously crafted image file. Any operation that reads or identifies an image can trigger the overflow, making it exploitable via common image upload and processing pipelines. Versions 7.1.2-13 and 6.9.13-38 fix the issue.

## References
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-23876.json
- https://access.redhat.com/errata/RHSA-2026:3058
- https://access.redhat.com/security/cve/CVE-2026-23876
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/23xxx/CVE-2026-23876.json
- https://github.com/ImageMagick/ImageMagick/security/advisories/GHSA-r49w-jqq3-3gx8
- https://nvd.nist.gov/vuln/detail/CVE-2026-23876
- https://bugzilla.redhat.com/show_bug.cgi?id=2431038
- https://github.com/ImageMagick/ImageMagick/commit/2fae24192b78fdfdd27d766fd21d90aeac6ea8b8
