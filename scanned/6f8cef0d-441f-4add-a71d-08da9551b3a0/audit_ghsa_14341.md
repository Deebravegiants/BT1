# [C] Remote code execution in broccoli-compass

## Summary
Severity: Critical
Advisory: GHSA-wq8f-xmq3-5vq9
CVE: CVE-2023-27848
CWE: CWE-77
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-04-24
Source: https://github.com/advisories/GHSA-wq8f-xmq3-5vq9
Type: github-advisory

## Affected
- npm: `broccoli-compass` — affected >=0

## Details
broccoli-compass v0.2.4 was discovered to contain a remote code execution (RCE) vulnerability via the child_process function.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-27848
- https://github.com/omnitaint/Vulnerability-Reports/blob/9d65add2bca71ed6d6b2e281ee6790a12504ff8e/reports/broccoli-compass/report.md
- https://www.npmjs.com/package/broccoli-compass
