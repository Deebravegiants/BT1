# [M] Uncontrolled resource consumption in jpeg-js

## Summary
Severity: Medium
Advisory: GHSA-w7q9-p3jq-fmhm
CVE: CVE-2020-8175
CWE: CWE-400
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2020-07-27
Source: https://github.com/advisories/GHSA-w7q9-p3jq-fmhm
Type: github-advisory

## Affected
- npm: `jpeg-js` — affected >=0 <0.4.0

## Details
Uncontrolled resource consumption in `jpeg-js` before 0.4.0 may allow attacker to launch denial of service attacks using specially a crafted JPEG image.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-8175
- https://github.com/eugeneware/jpeg-js/commit/135705b1510afb6cb4275a4655d92c58f6843e79
- https://hackerone.com/reports/842462
