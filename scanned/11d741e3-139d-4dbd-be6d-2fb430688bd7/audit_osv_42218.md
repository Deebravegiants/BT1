# [M] CVE-2026-65645

## Summary
Severity: Medium
Advisory: CVE-2026-65645
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2026-08-21
Source: https://osv.dev/vulnerability/CVE-2026-65645
Type: osv

## Details
Rocket.Chat in versions before 8.8.0, 8.7.1, 8.6.2, 8.5.3, 8.4.6. 8.3.8, 8.2.8, 8.1.8, and 7.10.15, the Meteor DDP methods getThreadsList and getThreadMessages accept rid / tmid as raw, untyped parameters with no schema validation. A MongoDB operator object (e.g. {"$gt": "4"}) can be substituted for a string room-id or message-id. The authorization check resolves to a room the attacker already has access to, while the downstream data query fans out across all rooms - disclosing private thread parents and their full reply content to any low-privilege authenticated user.
The REST route chat.getThreadsList was patched in v5.0 (HackerOne report #1446767) by adding rid: {type:'string'} AJV validation. The equivalent DDP method was never given the same fix and remains exploitable

## References
- https://hackerone.com/reports/3852135
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/65xxx/CVE-2026-65645.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-65645
- https://github.com/RocketChat/Rocket.Chat/pull/41814
