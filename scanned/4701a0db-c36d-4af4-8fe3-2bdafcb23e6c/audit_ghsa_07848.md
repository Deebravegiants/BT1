# [H] RaspAP raspap-webgui contains an OS Command Injection vulnerability

## Summary
Severity: High
Advisory: GHSA-4wwf-f7w3-94f5
CVE: CVE-2026-24788
CWE: CWE-78
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-02-02
Source: https://github.com/advisories/GHSA-4wwf-f7w3-94f5
Type: github-advisory

## Affected
- Packagist: `billz/raspap-webgui` — affected >=0 <3.3.6

## Details
RaspAP raspap-webgui versions prior to 3.3.6 contain an OS Command Injection vulnerability. If exploited, an arbitrary OS command may be executed by a user who can log in to the product.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-24788
- https://github.com/RaspAP/raspap-webgui/commit/f514f5a12ef0c34853b5370ef55d630b499f977d
- https://github.com/RaspAP/raspap-webgui
- https://github.com/RaspAP/raspap-webgui/releases/tag/3.3.6
- https://jvn.jp/en/jp/JVN27202136
