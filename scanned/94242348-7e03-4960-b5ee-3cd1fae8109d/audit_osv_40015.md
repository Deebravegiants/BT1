# [H] Apache Answer: Unauthenticated OAuth Email-Binding Account Takeover via Existing User Confirmation Flow

## Summary
Severity: High
Advisory: CVE-2026-48911
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2026-08-05
Source: https://osv.dev/vulnerability/CVE-2026-48911
Type: osv

## Details
Insufficient Verification of Data Authenticity vulnerability in Apache Answer.

This issue affects Apache Answer: through 2.0.1.

A missing authorization check in the external-login email binding flow allows unauthenticated attackers to take over arbitrary user accounts by tricking victims into clicking a crafted confirmation link.
Users are recommended to upgrade to version 2.0.2, which fixes the issue.

## References
- http://www.openwall.com/lists/oss-security/2026/08/05/10
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/48xxx/CVE-2026-48911.json
- https://lists.apache.org/thread/mrlwtdnhqqgfbchjgq6rffkz67o8wyv8
- https://nvd.nist.gov/vuln/detail/CVE-2026-48911
