# [H] Kotaemon Missing Ownership Check in Conversation Functions

## Summary
Severity: High
Advisory: CVE-2026-82281
CVSS: 7.5 (CVSS:4.0/AV:N/AC:H/AT:P/PR:N/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-28
Source: https://osv.dev/vulnerability/CVE-2026-82281
Type: osv

## Details
Kotaemon through 0.12.0 fails to properly validate conversation ownership in select_conv, delete_conv, rename_conv, and on_set_public_conversation functions in control.py. Attackers can read other users' chat histories, delete conversations, or rename conversations by supplying arbitrary conversation identifiers without proper authorization checks.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/82xxx/CVE-2026-82281.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-82281
- https://www.vulncheck.com/advisories/kotaemon-missing-ownership-check-in-conversation-functions
- https://github.com/Cinnamon/kotaemon/issues/846
- https://github.com/Cinnamon/kotaemon
- https://github.com/Cinnamon/kotaemon/blob/9ad3e4e49aa35b8acddd235918a5d9753c1cfdf9/libs/ktem/ktem/pages/chat/control.py
