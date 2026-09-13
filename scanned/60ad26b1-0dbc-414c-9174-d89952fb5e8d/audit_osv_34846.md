# [H] CVE-2025-65778

## Summary
Severity: High
Advisory: CVE-2025-65778
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:N)
Published: 2025-12-15
Source: https://osv.dev/vulnerability/CVE-2025-65778
Type: osv

## Details
An issue was discovered in Wekan The Open Source kanban board system up to version 18.15, fixed in 18.16. Uploaded attachments can be served with attacker-controlled Content-Type (text/html), allowing execution of attacker-supplied HTML/JS in the application's origin and enabling session/token theft and CSRF actions.

## References
- https://github.com/wekan/wekan/blob/main/CHANGELOG.md#v816-2025-11-02-wekan--release
- https://wekan.fi/hall-of-fame/spacebleed/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/65xxx/CVE-2025-65778.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-65778
- https://github.com/wekan/wekan/commit/e9a727301d7b4f1689a703503df668c0f4f4cab8
- https://github.com/wekan/wekan
