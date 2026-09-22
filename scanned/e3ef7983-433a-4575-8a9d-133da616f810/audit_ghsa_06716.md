# [M] morgan vulnerable to Log Forging via unneutralized control characters in :remote-user

## Summary
Severity: Medium
Advisory: GHSA-4vj7-5mj6-jm8m
CVE: CVE-2026-5078
CWE: CWE-117
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2026-07-10
Source: https://github.com/advisories/GHSA-4vj7-5mj6-jm8m
Type: github-advisory

## Affected
- npm: `morgan` — affected >=1.2.0 <1.11.0

## Details
### Impact

Morgan's `:remote-user` token extracts the Basic auth username from the `Authorization` header and writes it to the log stream without neutralizing control characters. An attacker can send a crafted `Authorization: Basic` header containing CR/LF characters to inject forged log lines, corrupting the one-request-per-line structure of access logs.

The built-in `combined`, `common`, `default`, and `short` formats are affected, as well as any custom format that includes `:remote-user`.

### Patches

Users should upgrade to version 1.11.0.

### Workarounds

Use a custom format string that does not include `:remote-user`.

## References
- https://github.com/expressjs/morgan/security/advisories/GHSA-4vj7-5mj6-jm8m
- https://nvd.nist.gov/vuln/detail/CVE-2026-5078
- https://cna.openjsf.org/security-advisories.html
- https://github.com/expressjs/morgan
