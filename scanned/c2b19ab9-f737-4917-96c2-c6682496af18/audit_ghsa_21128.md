# [C] ffmpeg-sdk vulnerable to OS Command Injection

## Summary
Severity: Critical
Advisory: GHSA-rwvf-c3wm-qm6w
CVE: CVE-2020-28435
CWE: CWE-77, CWE-78
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-07-26
Source: https://github.com/advisories/GHSA-rwvf-c3wm-qm6w
Type: github-advisory

## Affected
- npm: `ffmpeg-sdk` — affected >=0

## Details
A command injection vulnerability affects all versions of package ffmpeg-sdk. The injection point is located in line 9 in index.js.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-28435
- https://github.com/CubetLabs/ffmpeg-sdk/blob/master/index.js
- https://github.com/shajanjp/ffmpeg-sdk/blob/master/index.js
- https://security.snyk.io/vuln/SNYK-JS-FFMPEGSDK-1050429
