# [M] Cross-site scripting in TileServer GL

## Summary
Severity: Medium
Advisory: GHSA-3fr8-mwpp-8h9p
CVE: CVE-2020-15500
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2021-05-17
Source: https://github.com/advisories/GHSA-3fr8-mwpp-8h9p
Type: github-advisory

## Affected
- npm: `tileserver-gl` — affected >=0 <3.1.0

## Details
An issue was discovered in server.js in TileServer GL through 3.0.0. The content of the key GET parameter is reflected unsanitized in an HTTP response for the application's main page, causing reflected XSS.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-15500
- https://github.com/maptiler/tileserver-gl/issues/461
- https://github.com/maptiler/tileserver-gl/commit/10431d70d0f0d7b7950ae2c02aea0850c7566621
- https://github.com/maptiler/tileserver-gl
- http://packetstormsecurity.com/files/162193/Tileserver-gl-3.0.0-Cross-Site-Scripting.html
