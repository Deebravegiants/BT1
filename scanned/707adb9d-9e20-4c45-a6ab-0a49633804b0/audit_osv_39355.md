# [M] FreeScout Vulnerable to Unauthenticated Thread Read-Status Manipulation and Conversation Enumeration via Open Tracking Endpoint

## Summary
Severity: Medium
Advisory: CVE-2026-45295
Aliases: GHSA-qjr9-6v9q-3r72
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N)
Published: 2026-07-20
Source: https://osv.dev/vulnerability/CVE-2026-45295
Type: osv

## Details
FreeScout is a free help desk and shared inbox built with PHP's Laravel framework. Prior to version 1.8.219, the open tracking endpoint `GET /thread/read/{conversation_id}/{thread_id}` allows unauthenticated attackers to enumerate valid conversation and thread IDs, and modify thread state (`opened_at` timestamp) without any authentication. Version 1.8.219 patches the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/45xxx/CVE-2026-45295.json
- https://github.com/freescout-help-desk/freescout/security/advisories/GHSA-qjr9-6v9q-3r72
- https://nvd.nist.gov/vuln/detail/CVE-2026-45295
