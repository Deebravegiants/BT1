# [M] Apache Answer: Improper authorization in avatar update cleanup allows authenticated users to delete arbitrary uploaded files by URL

## Summary
Severity: Medium
Advisory: CVE-2026-48912
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N)
Published: 2026-08-05
Source: https://osv.dev/vulnerability/CVE-2026-48912
Type: osv

## Details
Improper Input Validation vulnerability in Apache Answer.

This issue affects Apache Answer: through 2.0.1.

 A missing ownership check in the avatar-cleanup logic allows any authenticated user to delete other users' uploaded files by supplying their file URLs.
Users are recommended to upgrade to version 2.0.2, which fixes the issue.

## References
- http://www.openwall.com/lists/oss-security/2026/08/05/11
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/48xxx/CVE-2026-48912.json
- https://lists.apache.org/thread/b9jnttmspd9kp4vgbvb32dcqb4201flq
- https://nvd.nist.gov/vuln/detail/CVE-2026-48912
