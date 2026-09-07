# [M] gotortc Cross-site Scripting vulnerability

## Summary
Severity: Medium
Advisory: GHSA-rh4r-f7f7-r99m
CVE: CVE-2024-29193
CWE: CWE-79
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2024-08-05
Source: https://github.com/advisories/GHSA-rh4r-f7f7-r99m
Type: github-advisory

## Affected
- Go: `github.com/AlexxIT/go2rtc` — affected >=0 <1.9.0

## Details
gotortc is a camera streaming application. Versions 1.8.5 and prior are vulnerable to DOM-based cross-site scripting. The index page (`index.html`) shows the available streams by fetching the API in the client side. Then, it uses `Object.entries` to iterate over the result whose first item (`name`) gets appended using `innerHTML`. In the event of a victim visiting the server in question, their browser will execute the request against the go2rtc instance. After the request, the browser will be redirected to go2rtc, in which the XSS would be executed in the context of go2rtc’s origin.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-29193
- https://github.com/AlexxIT/go2rtc/commit/3b3d5b033aac3a019af64f83dec84f70ed2c8aba
- https://github.com/AlexxIT/go2rtc
- https://securitylab.github.com/advisories/GHSL-2023-205_GHSL-2023-207_go2rtc
