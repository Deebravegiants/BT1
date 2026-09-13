# [H] snipe-IT vulnerable to host header injection

## Summary
Severity: High
Advisory: GHSA-9vh6-qfv6-vcqp
CVE: CVE-2022-23064
CWE: CWE-74
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-03
Source: https://github.com/advisories/GHSA-9vh6-qfv6-vcqp
Type: github-advisory

## Affected
- Packagist: `snipe/snipe-it` — affected >=3.0-alpha <5.4.0

## Details
Snipe-IT is a free, open-source IT asset/license management systemIn Snipe-IT, versions v3.0-alpha to v5.3.7 are vulnerable to Host Header Injection. By sending a specially crafted host header in the reset password request, it is possible to send password reset links to users which once clicked lead to an attacker controlled server and thus leading to password reset token leak. This can lead to account take over.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-23064
- https://github.com/snipe/snipe-it/commit/0c4768fd2a11ac26a61814cef23a71061bfd8bcc
- https://github.com/snipe/snipe-it
- https://www.whitesourcesoftware.com/vulnerability-database/CVE-2022-23064
