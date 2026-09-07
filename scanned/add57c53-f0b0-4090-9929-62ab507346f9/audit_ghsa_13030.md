# [M] Critters Cross-site Scripting Vulnerability

## Summary
Severity: Medium
Advisory: GHSA-cx3j-qqxj-9597
CVE: CVE-2023-3481
CWE: CWE-116, CWE-79, CWE-80
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2023-08-11
Source: https://github.com/advisories/GHSA-cx3j-qqxj-9597
Type: github-advisory

## Affected
- npm: `critters` — affected >=0.0.17 <0.0.20

## Details
### Impact
Critters version 0.0.17-0.0.19 have an issue when parsing the HTML which leads to a potential [cross-site scripting (XSS)](https://owasp.org/www-community/attacks/xss/) bug.

### Patches
The bug has been fixed in `v0.0.20`.

### Workarounds
Upgrading Critters version to `>0.0.20` is the easiest fix. This is a non breaking version upgrade so we recommend all users to use `v0.0.20`.

## References
- https://github.com/GoogleChromeLabs/critters/security/advisories/GHSA-cx3j-qqxj-9597
- https://nvd.nist.gov/vuln/detail/CVE-2023-3481
- https://github.com/GoogleChromeLabs/critters/pull/133
- https://github.com/GoogleChromeLabs/critters/commit/7757902c9e0b3285d516359b3cb602cd9d50d80e
- https://github.com/GoogleChromeLabs/critters
