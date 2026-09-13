# [C] Command Injection in ffmpegdotjs

## Summary
Severity: Critical
Advisory: GHSA-f39r-cpmj-whcg
CVE: CVE-2021-23376
CWE: CWE-77
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-05-06
Source: https://github.com/advisories/GHSA-f39r-cpmj-whcg
Type: github-advisory

## Affected
- npm: `ffmpegdotjs` — affected >=0

## Details
This affects all versions of package ffmpegdotjs. If attacker-controlled user input is given to the trimvideo function, it is possible for an attacker to execute arbitrary commands. This is due to use of the child_process exec function without input sanitization.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-23376
- https://github.com/TRomesh/ffmpegdotjs
- https://github.com/TRomesh/ffmpegdotjs/blob/b7395daf0bdcb81218340427eb7073cdd28462af/index.js#23L219
- https://snyk.io/vuln/SNYK-JS-FFMPEGDOTJS-1078542
