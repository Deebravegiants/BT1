# [M] Awesome Support vulnerable to persistent cross-site scripting

## Summary
Severity: Medium
Advisory: GHSA-qrqm-574x-q7f2
CVE: CVE-2022-38073
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-09-22
Source: https://github.com/advisories/GHSA-qrqm-574x-q7f2
Type: github-advisory

## Affected
- Packagist: `awesome-support/awesome-support` — affected >=0 <6.0.8

## Details
Multiple Authenticated (custom specific plugin role) Persistent Cross-Site Scripting (XSS) vulnerability in Awesome Support plugin <= 6.0.7 at WordPress.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-38073
- https://github.com/Awesome-Support/Awesome-Support/commit/85f460be88b81fbdd9a990f474a1252297902faf
- https://github.com/Awesome-Support/Awesome-Support/commit/b2e831d7f831a3869cfd83eb79a398a5b5c0ec63
- https://github.com/Awesome-Support/Awesome-Support
- https://patchstack.com/database/vulnerability/awesome-support/wordpress-awesome-support-plugin-6-0-7-multiple-authenticated-stored-cross-site-scripting-xss-vulnerabilities
- https://wordpress.org/plugins/awesome-support/#developers
