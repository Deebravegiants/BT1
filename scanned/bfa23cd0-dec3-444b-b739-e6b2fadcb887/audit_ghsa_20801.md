# [M] Microweber vulnerable to  HTML Injection in create tag functionality

## Summary
Severity: Medium
Advisory: GHSA-gm8c-w9cm-c445
CVE: CVE-2022-3245
CWE: CWE-79, CWE-94
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-09-21
Source: https://github.com/advisories/GHSA-gm8c-w9cm-c445
Type: github-advisory

## Affected
- Packagist: `microweber/microweber` — affected >=0 <1.3.2

## Details
HTML injection attack is closely related to Cross-site Scripting (XSS). HTML injection uses HTML to deface the page. XSS, as the name implies, injects JavaScript into the page. Both attacks exploit insufficient validation of user input. A patch is available on commit f20abf30a1d9c1426c5fb757ac63998dc5b92bfc and is anticipated to be part of version 1.3.2.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-3245
- https://github.com/microweber/microweber/commit/f20abf30a1d9c1426c5fb757ac63998dc5b92bfc
- https://github.com/microweber/microweber
- https://huntr.dev/bounties/747c2924-95ca-4311-9e69-58ee0fb440a0
