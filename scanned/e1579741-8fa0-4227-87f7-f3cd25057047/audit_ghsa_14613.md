# [M] tecnickcom/tc-lib-pdf-font mishandles fonts

## Summary
Severity: Medium
Advisory: GHSA-grhh-r4jj-8jh7
CVE: CVE-2024-56520
Ecosystem: Packagist
Published: 2024-12-27
Source: https://github.com/advisories/GHSA-grhh-r4jj-8jh7
Type: github-advisory

## Affected
- Packagist: `tecnickcom/tc-lib-pdf-font` — affected >=0 <2.6.4

## Details
An issue was discovered in tc-lib-pdf-font before 2.6.4, as used in TCPDF before 6.8.0 and other products. Fonts are mishandled, e.g., FontBBox for Type 1 and TrueType fonts is misparsed.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-56520
- https://github.com/tecnickcom/TCPDF/commit/a0a02efe487cc39bd5223359e916dbeafb5cd6fe
- https://github.com/tecnickcom/tc-lib-pdf-font/commit/30012e333ae611c514ec2dc7cb370bbf4da4e677
- https://github.com/tecnickcom/TCPDF/compare/6.7.8...6.8.0
- https://github.com/tecnickcom/tc-lib-pdf-font
- https://github.com/tecnickcom/tc-lib-pdf-font/compare/2.6.2...2.6.4
- https://lists.debian.org/debian-lts-announce/2025/06/msg00004.html
- https://tcpdf.org
