# [M] JLSEC-2026-902

## Summary
Severity: Medium
Advisory: JLSEC-2026-902
Ecosystem: Julia
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2026-07-30
Source: https://osv.dev/vulnerability/JLSEC-2026-902
Type: osv

## Affected
- Julia: `ImageMagick_jll` — affected >=0 <6.9.12+4

## Details
A heap-based buffer overflow issue was discovered in ImageMagick's ImportMultiSpectralQuantum() function in `MagickCore/quantum-import.c`. An attacker could pass specially crafted file to convert, triggering an out-of-bounds read error, allowing an application to crash, resulting in a denial of service.

## References
- https://access.redhat.com/security/cve/CVE-2023-1906
- https://access.redhat.com/security/cve/CVE-2023-1906
- https://bugzilla.redhat.com/show_bug.cgi?id=2185714
- https://bugzilla.redhat.com/show_bug.cgi?id=2185714
- https://github.com/ImageMagick/ImageMagick/commit/d7a8bdd7bb33cf8e58bc01b4a4f2ea5466f8c6b3
- https://github.com/ImageMagick/ImageMagick/commit/d7a8bdd7bb33cf8e58bc01b4a4f2ea5466f8c6b3
- https://github.com/ImageMagick/ImageMagick/security/advisories/GHSA-35q2-86c7-9247
- https://github.com/ImageMagick/ImageMagick/security/advisories/GHSA-35q2-86c7-9247
- https://github.com/ImageMagick/ImageMagick6/commit/e30c693b37c3b41723f1469d1226a2c814ca443d
- https://github.com/ImageMagick/ImageMagick6/commit/e30c693b37c3b41723f1469d1226a2c814ca443d
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/6655G3GPS42WQM32DJHUCZALI2URQSCO/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/6655G3GPS42WQM32DJHUCZALI2URQSCO/
