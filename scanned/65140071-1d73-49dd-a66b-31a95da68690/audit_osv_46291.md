# [C] JLSEC-2026-936

## Summary
Severity: Critical
Advisory: JLSEC-2026-936
Ecosystem: Julia
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-30
Source: https://osv.dev/vulnerability/JLSEC-2026-936
Type: osv

## Affected
- Julia: `ImageMagick_jll` — affected >=0 <7.1.2023+0

## Details
ImageMagick is free and open-source software used for editing and manipulating digital images. Prior to versions 7.1.2-13 and 6.9.13-38, a heap buffer overflow vulnerability in the XBM image decoder (ReadXBMImage) allows an attacker to write controlled data past the allocated heap buffer when processing a maliciously crafted image file. Any operation that reads or identifies an image can trigger the overflow, making it exploitable via common image upload and processing pipelines. Versions 7.1.2-13 and 6.9.13-38 fix the issue.

## References
- https://access.redhat.com/errata/RHSA-2026:3058
- https://access.redhat.com/security/cve/CVE-2026-23876
- https://bugzilla.redhat.com/show_bug.cgi?id=2431038
- https://github.com/ImageMagick/ImageMagick/commit/2fae24192b78fdfdd27d766fd21d90aeac6ea8b8
- https://github.com/ImageMagick/ImageMagick/security/advisories/GHSA-r49w-jqq3-3gx8
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-23876.json
