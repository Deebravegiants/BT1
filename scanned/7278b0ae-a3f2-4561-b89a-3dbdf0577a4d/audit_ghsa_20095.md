# [H] Jettison Out-of-bounds Write vulnerability

## Summary
Severity: High
Advisory: GHSA-grr4-wv38-f68w
CVE: CVE-2022-45693
CWE: CWE-787
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-12-13
Source: https://github.com/advisories/GHSA-grr4-wv38-f68w
Type: github-advisory

## Affected
- Maven: `org.codehaus.jettison:jettison` — affected >=0 <1.5.2

## Details
Jettison before v1.5.2 was discovered to contain a stack overflow via the map parameter. This vulnerability allows attackers to cause a Denial of Service (DoS) via a crafted string.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-45693
- https://github.com/jettison-json/jettison/issues/52
- https://github.com/jettison-json/jettison
- https://lists.debian.org/debian-lts-announce/2022/12/msg00045.html
- https://www.debian.org/security/2023/dsa-5312
