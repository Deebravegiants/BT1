# [H] Live Helper Chat: REST API chat update accepts arbitrary chat fields across department boundaries

## Summary
Severity: High
Advisory: CVE-2026-44633
Aliases: GHSA-hjqq-qmvj-9whm
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N)
Published: 2026-05-14
Source: https://osv.dev/vulnerability/CVE-2026-44633
Type: osv

## Details
Live Helper Chat is an open-source application that enables live support websites. In 4.84v, the Live Helper Chat REST API chat update endpoint allows a REST user with lhchat/use to update a chat in a department they cannot read. The endpoint accepts arbitrary chat object fields, so the user can change the chat hash and status and then access or tamper with the chat through visitor/widget paths. The same write primitive can set operation_admin, which is later emitted as operator-side JavaScript.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/44xxx/CVE-2026-44633.json
- https://github.com/LiveHelperChat/livehelperchat/security/advisories/GHSA-hjqq-qmvj-9whm
- https://nvd.nist.gov/vuln/detail/CVE-2026-44633
