# [M] Simple Machines Forum Authorization Bypass via AttachmentApprove.php

## Summary
Severity: Medium
Advisory: CVE-2026-39903
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:H/VA:L/SC:N/SI:N/SA:N)
Published: 2026-07-10
Source: https://osv.dev/vulnerability/CVE-2026-39903
Type: osv

## Details
Simple Machines Forum 2.1 prior to commit 7d048f8 and 3.0 prior to commit a7875e8 contains an authorization bypass vulnerability in Sources/Actions/AttachmentApprove.php where a single-character operator error causes the permission check to always pass regardless of user permissions. An authenticated low-privileged user can approve, reject, or delete any pending attachments on any board without holding the required approve_posts permission, bypass moderation queues for their own uploads, and enumerate and delete other users' pending attachments.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/39xxx/CVE-2026-39903.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-39903
- https://www.vulncheck.com/advisories/simple-machines-forum-authorization-bypass-via-attachmentapprove-php
- https://github.com/SimpleMachines/SMF/pull/9181
- https://github.com/SimpleMachines/SMF/pull/9182
- https://github.com/SimpleMachines/SMF/commit/7d048f8d66aab9af51cd6ee110fbad103cf673e8
- https://github.com/SimpleMachines/SMF/commit/a7875e876a647572dd4c45da881b875092caac3d
- https://github.com/SimpleMachines/SMF
