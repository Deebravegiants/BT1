# [M] TCPDF vulnerable to Regular Expression Denial of Service

## Summary
Severity: Medium
Advisory: GHSA-mx3p-fhpw-x6rv
CVE: CVE-2024-22640
CWE: CWE-1333
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2024-04-19
Source: https://github.com/advisories/GHSA-mx3p-fhpw-x6rv
Type: github-advisory

## Affected
- Packagist: `tecnickcom/tcpdf` — affected >=0 <6.7.5

## Details
TCPDF version <= 6.7.4 is vulnerable to ReDoS (Regular Expression Denial of Service) if parsing an untrusted HTML page with a crafted color.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-22640
- https://github.com/tecnickcom/TCPDF/commit/05f3a28f4a7905019469e040cf77e53d6aa7f679
- https://github.com/tecnickcom/TCPDF
- https://github.com/zunak/CVE-2024-22640
- https://lists.debian.org/debian-lts-announce/2025/06/msg00004.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/LIB3R2WB7XPW2I4PGVMZ3VLFLRHOK4RB
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/LIB3R2WB7XPW2I4PGVMZ3VLFLRHOK4RB
