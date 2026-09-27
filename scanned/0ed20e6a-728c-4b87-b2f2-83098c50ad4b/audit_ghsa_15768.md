# [H] @amoy/common v was discovered to contain a prototype pollution via the function extend

## Summary
Severity: High
Advisory: GHSA-w58v-r3cp-qr93
CVE: CVE-2024-38994
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2024-07-01
Source: https://github.com/advisories/GHSA-w58v-r3cp-qr93
Type: github-advisory

## Affected
- npm: `@amoy/common` — affected 1.0.10

## Details
amoyjs amoy common v1.0.10 was discovered to contain a prototype pollution via the function extend. This vulnerability allows attackers to execute arbitrary code or cause a Denial of Service (DoS) via injecting arbitrary properties.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-38994
- https://gist.github.com/mestrtee/02091aa86c6c14c29b9703642439dd03
