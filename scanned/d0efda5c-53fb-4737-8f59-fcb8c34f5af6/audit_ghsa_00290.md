# [M] Stored Cross-Site Scripting in simplehttpserver

## Summary
Severity: Medium
Advisory: GHSA-jrhj-2j3q-xf3v
CVE: CVE-2018-3716
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2018-07-26
Source: https://github.com/advisories/GHSA-jrhj-2j3q-xf3v
Type: github-advisory

## Affected
- npm: `simplehttpserver` — affected >=0 <0.1.0

## Details
Simplehttpserver prior to version 0.1.0 are vulnerable to stored cross-site scripting (XSS). To be exploited an attacker needs to control the filename of a file that is used in the directory listing output. This version is patched in 0.1.0

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-3716
- https://hackerone.com/reports/309648
- https://github.com/advisories/GHSA-jrhj-2j3q-xf3v
- https://www.npmjs.com/advisories/585
