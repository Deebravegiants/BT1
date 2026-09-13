# [H] Jettison memory exhaustion

## Summary
Severity: High
Advisory: GHSA-x27m-9w8j-5vcw
CVE: CVE-2022-40150
CWE: CWE-400, CWE-674
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-09-17
Source: https://github.com/advisories/GHSA-x27m-9w8j-5vcw
Type: github-advisory

## Affected
- Maven: `org.codehaus.jettison:jettison` — affected >=0 <1.5.2

## Details
Those using Jettison to parse untrusted XML or JSON data may be vulnerable to Denial of Service attacks (DOS). If the parser is running on user supplied input, an attacker may supply content that causes the parser to crash by Out of memory. This effect may support a denial of service attack.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-40150
- https://github.com/jettison-json/jettison/issues/45
- https://bugs.chromium.org/p/oss-fuzz/issues/detail?id=46549
- https://github.com/jettison-json/jettison
- https://lists.debian.org/debian-lts-announce/2022/12/msg00045.html
- https://www.debian.org/security/2023/dsa-5312
