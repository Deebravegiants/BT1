# [M] FreeScout: Thread Deletion Bypasses Mailbox Access Revocation

## Summary
Severity: Medium
Advisory: CVE-2026-48811
Aliases: GHSA-9vx8-gx3p-9mh6
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N)
Published: 2026-05-29
Source: https://osv.dev/vulnerability/CVE-2026-48811
Type: osv

## Details
FreeScout is a free help desk and shared inbox built with PHP's Laravel framework. Prior to 1.8.221, FreeScout allows a non-admin user to permanently delete an internal note (private thread) from any conversation, even after that user's access to the mailbox containing the conversation has been revoked. The ThreadPolicy::delete authorization policy does not verify mailbox membership, so a former team member retains destructive write access to notes they created. This vulnerability is fixed in 1.8.221.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/48xxx/CVE-2026-48811.json
- https://github.com/freescout-help-desk/freescout/security/advisories/GHSA-9vx8-gx3p-9mh6
- https://nvd.nist.gov/vuln/detail/CVE-2026-48811
