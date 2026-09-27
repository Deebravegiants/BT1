# [M] Apache Answer: Missing authorization in revision audit reject allows authenticated users to reject pending revisions

## Summary
Severity: Medium
Advisory: CVE-2026-50749
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N)
Published: 2026-08-05
Source: https://osv.dev/vulnerability/CVE-2026-50749
Type: osv

## Details
Improper Authorization vulnerability in Apache Answer.

This issue affects Apache Answer: through 2.0.1.

Any authenticated user can reject arbitrary pending edit-revisions without review permission due to a missing authorization check on the reject operation.
Users are recommended to upgrade to version 2.0.2, which fixes the issue.

## References
- http://www.openwall.com/lists/oss-security/2026/08/05/12
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/50xxx/CVE-2026-50749.json
- https://lists.apache.org/thread/ogk461yr4w9o95k15bkjxk2kpbkrbnln
- https://nvd.nist.gov/vuln/detail/CVE-2026-50749
