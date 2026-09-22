# [C] Unrestricted Upload of File with Dangerous Type in Zenario CMS

## Summary
Severity: Critical
Advisory: GHSA-rgg3-3wh7-w935
CVE: CVE-2021-42171
CWE: CWE-434
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-03-15
Source: https://github.com/advisories/GHSA-rgg3-3wh7-w935
Type: github-advisory

## Affected
- Packagist: `tribalsystems/zenario` — affected >=0 <9.0.55143

## Details
Zenario CMS 9.0.54156 is vulnerable to File Upload. The web server can be compromised by uploading and executing a web-shell which can run commands, browse system files, browse local resources, attack other servers, and exploit the local vulnerabilities, and so forth.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-42171
- https://github.com/hieuminhnv/Zenario-CMS-9.0-last-version/issues/2
- https://github.com/TribalSystems/Zenario/commit/4566d8a9ac6755f098b3373252fdb17754a77007
- https://github.com/TribalSystems/Zenario
- https://github.com/TribalSystems/Zenario/releases/tag/9.0.55141
- https://minhnq22.medium.com/file-upload-to-rce-on-zenario-9-0-54156-cms-fa05fcc6cf74
- http://packetstormsecurity.com/files/166617/Zenario-CMS-9.0.54156-Remote-Code-Execution.html
