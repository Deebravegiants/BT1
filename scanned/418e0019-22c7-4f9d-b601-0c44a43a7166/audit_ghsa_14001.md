# [H] Command injection in nevado-jms

## Summary
Severity: High
Advisory: GHSA-7gm3-mwjw-j53w
CVE: CVE-2023-31826
CWE: CWE-862
Ecosystem: Maven
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-05-23
Source: https://github.com/advisories/GHSA-7gm3-mwjw-j53w
Type: github-advisory

## Affected
- Maven: `org.skyscreamer:nevado-jms` — affected >=0

## Details
Skyscreamer Open Source Nevado JMS v1.3.2 does not perform security checks when receiving messages. This allows attackers to execute arbitrary commands via supplying crafted data.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-31826
- https://github.com/skyscreamer/nevado/issues/121
- https://github.com/skyscreamer/nevado
- https://github.com/skyscreamer/nevado/releases
- https://novysodope.github.io/2023/04/01/95
- http://nevado.skyscreamer.org
