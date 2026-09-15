# [H] Cherry Studio One-click Remote Code Execution Vulnerability through Custom URL Handling

## Summary
Severity: High
Advisory: CVE-2025-54063
Aliases: GHSA-p6vw-w3p8-4g72
CVSS: 8.0 (CVSS:3.1/AV:A/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2025-08-11
Source: https://osv.dev/vulnerability/CVE-2025-54063
Type: osv

## Details
Cherry Studio is a desktop client that supports for multiple LLM providers. From versions 1.4.8 to 1.5.0, there is a one-click remote code execution vulnerability through the custom URL handling. An attacker can exploit this by hosting a malicious website or embedding a specially crafted URL on any website. If a victim clicks the exploit link in their browser, the app’s custom URL handler is triggered, leading to remote code execution on the victim’s machine. This issue has been patched in version 1.5.1.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/54xxx/CVE-2025-54063.json
- https://github.com/CherryHQ/cherry-studio/security/advisories/GHSA-p6vw-w3p8-4g72
- https://nvd.nist.gov/vuln/detail/CVE-2025-54063
- https://github.com/CherryHQ/cherry-studio/commit/ff72c007c03ff47de21a4d0bf52a1ff1fb35cd89
- https://github.com/CherryHQ/cherry-studio/pull/8218
