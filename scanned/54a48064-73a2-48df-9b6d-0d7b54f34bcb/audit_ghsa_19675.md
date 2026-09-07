# [M] LocalAI Cross-Site Scripting (XSS) vulnerability in its search functionality

## Summary
Severity: Medium
Advisory: GHSA-w6hh-w36c-vxmw
CVE: CVE-2024-9900
CWE: CWE-115, CWE-79
Ecosystem: Go
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2025-03-20
Source: https://github.com/advisories/GHSA-w6hh-w36c-vxmw
Type: github-advisory

## Affected
- Go: `github.com/mudler/LocalAI` — affected >=0 <2.22.0

## Details
mudler/localai version v2.21.1 contains a Cross-Site Scripting (XSS) vulnerability in its search functionality. The vulnerability arises due to improper sanitization of user input, allowing the injection and execution of arbitrary JavaScript code. This can lead to the execution of malicious scripts in the context of the victim's browser, potentially compromising user sessions, stealing session cookies, redirecting users to malicious websites, or manipulating the DOM.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-9900
- https://github.com/mudler/localai/commit/a1634b219a4e52813e70ff07e6376a01449c4515
- https://github.com/mudler/LocalAI
- https://huntr.com/bounties/b39cd230-db66-471b-89b9-24afaa078e68
