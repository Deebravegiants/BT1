# [M] Cross-site Scripting in Jirafeau

## Summary
Severity: Medium
Advisory: GHSA-j2xf-p274-g8cc
CVE: CVE-2022-30110
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-18
Source: https://github.com/advisories/GHSA-j2xf-p274-g8cc
Type: github-advisory

## Affected
- Packagist: `mojo42/jirafeau` — affected >=0 <4.4.0

## Details
The file preview functionality in Jirafeau < 4.4.0, which is enabled by default, could be exploited for cross site scripting. An attacker could upload image/svg+xml files containing JavaScript. When someone visits the File Preview URL for this file, the JavaScript inside of this image/svg+xml file will be executed in the users' browser.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-30110
- https://gitlab.com/mojo42/Jirafeau
- https://gitlab.com/mojo42/Jirafeau/-/merge_requests/103
