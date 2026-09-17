# [C] thumbler allows OS Command Injection

## Summary
Severity: Critical
Advisory: GHSA-mvhf-547c-h55r
CVE: CVE-2026-26833
CWE: CWE-78, CWE-94
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-03-25
Source: https://github.com/advisories/GHSA-mvhf-547c-h55r
Type: github-advisory

## Affected
- npm: `thumbler` — affected >=0

## Details
thumbler through 1.1.2 allows OS command injection via the input, output, time, or size parameter in the thumbnail() function because user input is concatenated into a shell command string passed to child_process.exec() without proper sanitization or escaping.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-26833
- https://github.com/mmahrous/thumbler
- https://github.com/mmahrous/thumbler/blob/master/lib/thumbler.js
- https://github.com/zebbernCVE/CVE-2026-26833
- https://www.npmjs.com/package/thumbler
