# [H] Buffer overflow  in canvas

## Summary
Severity: High
Advisory: GHSA-73rg-x683-m3qw
CVE: CVE-2020-8215
CWE: CWE-120
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-05-07
Source: https://github.com/advisories/GHSA-73rg-x683-m3qw
Type: github-advisory

## Affected
- npm: `canvas` — affected >=0 <1.6.11

## Details
A buffer overflow is present in canvas versions before 1.6.11, which could lead to a Denial of Service or execution of arbitrary code when it processes a user-provided image.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-8215
- https://github.com/Automattic/node-canvas/commit/c3e4ccb1c404da01e83fe5eb3626bf55f7f55957
- https://hackerone.com/reports/315037
- https://www.npmjs.com/package/canvas
