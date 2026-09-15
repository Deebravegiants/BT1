# [M] CVE-2023-1906

## Summary
Severity: Medium
Advisory: CVE-2023-1906
Aliases: GHSA-35q2-86c7-9247
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2023-04-12
Source: https://osv.dev/vulnerability/CVE-2023-1906
Type: osv

## Details
A heap-based buffer overflow issue was discovered in ImageMagick's ImportMultiSpectralQuantum() function in MagickCore/quantum-import.c. An attacker could pass specially crafted file to convert, triggering an out-of-bounds read error, allowing an application to crash, resulting in a denial of service.

## References
- https://access.redhat.com/security/cve/CVE-2023-1906
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/1xxx/CVE-2023-1906.json
- https://github.com/ImageMagick/ImageMagick/security/advisories/GHSA-35q2-86c7-9247
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/6655G3GPS42WQM32DJHUCZALI2URQSCO/
- https://nvd.nist.gov/vuln/detail/CVE-2023-1906
- https://bugzilla.redhat.com/show_bug.cgi?id=2185714
- https://github.com/ImageMagick/ImageMagick/commit/d7a8bdd7bb33cf8e58bc01b4a4f2ea5466f8c6b3
- https://github.com/ImageMagick/ImageMagick6/commit/e30c693b37c3b41723f1469d1226a2c814ca443d
