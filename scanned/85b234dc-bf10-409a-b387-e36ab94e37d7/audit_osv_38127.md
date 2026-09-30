# [M] Scoold: Cross-Account Feedback Deletion (IDOR)

## Summary
Severity: Medium
Advisory: CVE-2026-34832
Aliases: GHSA-g5fv-xw88-vw44
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N)
Published: 2026-04-02
Source: https://osv.dev/vulnerability/CVE-2026-34832
Type: osv

## Details
Scoold is a Q&A and a knowledge sharing platform for teams. Prior to version 1.66.1, Scoold contains an authenticated authorization flaw in feedback deletion that allows any logged-in, low-privilege user to delete another user's feedback post by submitting its ID to POST /feedback/{id}/delete. The handler enforces authentication but does not enforce object ownership (or moderator/admin authorization) before deletion. In verification, a second non-privileged account successfully deleted a victim account's feedback item, and the item immediately disappeared from the feedback listing/detail views. This issue has been patched in version 1.66.1.

## References
- https://github.com/Erudika/scoold/releases/tag/1.66.1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/34xxx/CVE-2026-34832.json
- https://github.com/Erudika/scoold/security/advisories/GHSA-g5fv-xw88-vw44
- https://nvd.nist.gov/vuln/detail/CVE-2026-34832
- https://github.com/Erudika/scoold/commit/5def88c25405cc60482292bcceb45dc024e899fe
