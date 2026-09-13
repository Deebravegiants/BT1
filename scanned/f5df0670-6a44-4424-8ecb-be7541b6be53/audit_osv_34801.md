# [M] ClipBucket v5 Unauthenticated Object Flagging Vulnerability

## Summary
Severity: Medium
Advisory: CVE-2025-65113
Aliases: GHSA-9f8v-vph8-pq6q
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:L)
Published: 2025-11-29
Source: https://osv.dev/vulnerability/CVE-2025-65113
Type: osv

## Details
ClipBucket v5 is an open source video sharing platform. Prior to version 5.5.2 - #164, an authorization bypass vulnerability in the AJAX flagging system allows any unauthenticated user to flag any content (users, videos, photos, collections) on the platform. This can lead to mass flagging attacks, content disruption, and moderation system abuse. This issue has been patched in version 5.5.2 - #164.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/65xxx/CVE-2025-65113.json
- https://github.com/MacWarrior/clipbucket-v5/security/advisories/GHSA-9f8v-vph8-pq6q
- https://nvd.nist.gov/vuln/detail/CVE-2025-65113
- https://github.com/MacWarrior/clipbucket-v5/commit/a83b807e592f85d98f1f156bd3cbb1ffcc230233
