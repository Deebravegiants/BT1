# [H] Arbitrary application execution via unvalidated server-controlled URLs in Help menu

## Summary
Severity: High
Advisory: CVE-2026-1046
CVSS: 7.6 (CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:H/I:N/A:L)
Published: 2026-02-16
Source: https://osv.dev/vulnerability/CVE-2026-1046
Type: osv

## Details
Mattermost Desktop App versions <=6.0 6.2.0 5.2.13.0 fail to validate help links which allows a malicious Mattermost server to execute arbitrary executables on a user’s system via the user clicking on certain items in the Help menu Mattermost Advisory ID: MMSA-2026-00577

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/1xxx/CVE-2026-1046.json
- https://mattermost.com/security-updates
- https://nvd.nist.gov/vuln/detail/CVE-2026-1046
