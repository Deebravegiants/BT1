# [M] BrowserStack Local vulnerable to Command Injection through logfile variable

## Summary
Severity: Medium
Advisory: GHSA-g4w6-c99w-4wh7
CVE: CVE-2025-57283
CWE: CWE-77
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:H/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:P (CVSS_V4)
Published: 2026-01-28
Source: https://github.com/advisories/GHSA-g4w6-c99w-4wh7
Type: github-advisory

## Affected
- npm: `browserstack-local` — affected >=0 <1.5.9

## Details
The Node.js package browserstack-local 1.5.8 contains a command injection vulnerability. This occurs because the logfile variable is not properly sanitized in lib/Local.js.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-57283
- https://github.com/browserstack/browserstack-local-nodejs/issues/168
- https://gist.github.com/Dremig/b639c61541dd1482007dc7a5cd7fefb1
- https://github.com/browserstack/browserstack-local-nodejs
- https://www.npmjs.com
