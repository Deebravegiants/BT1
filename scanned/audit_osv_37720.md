# [H] CVE-2026-32995

## Summary
Severity: High
Advisory: CVE-2026-32995
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-05-28
Source: https://osv.dev/vulnerability/CVE-2026-32995
Type: osv

## Details
The Rocket.Chat DDP method autoTranslate.translateMessage in versions <8.5.0, <8.4.2, <8.3.4, <8.2.4, <8.1.5, <8.0.5, <7.13.8, and <7.10.12 accepts a client-supplied IMessage object and passes it directly to translateMessage() without checking Meteor.userId() or verifying room membership. Any authenticated DDP user can read the content of any message by ID from any room (private channels, DMs, E2EE rooms) by calling this method.

## References
- https://hackerone.com/reports/3734326
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/32xxx/CVE-2026-32995.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-32995
- https://github.com/RocketChat/Rocket.Chat/pull/40528
