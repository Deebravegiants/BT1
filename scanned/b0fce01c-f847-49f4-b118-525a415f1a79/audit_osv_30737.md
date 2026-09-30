# [M] phpMyFAQ Vulnerable to Unintended File Download Triggered by Embedded Frames

## Summary
Severity: Medium
Advisory: CVE-2024-55889
Aliases: GHSA-m3r7-8gw7-qwvc
CVSS: 4.9 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:N/I:H/A:N)
Published: 2024-12-13
Source: https://osv.dev/vulnerability/CVE-2024-55889
Type: osv

## Details
phpMyFAQ is an open source FAQ web application. Prior to version 3.2.10, a vulnerability exists in the FAQ Record component where a privileged attacker can trigger a file download on a victim's machine upon page visit by embedding it in an <iframe> element without user interaction or explicit consent. Version 3.2.10 fixes the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/55xxx/CVE-2024-55889.json
- https://github.com/thorsten/phpMyFAQ/security/advisories/GHSA-m3r7-8gw7-qwvc
- https://nvd.nist.gov/vuln/detail/CVE-2024-55889
- https://github.com/thorsten/phpMyFAQ/commit/fa0f7368dc3288eedb1915def64ef8fb270f711d
