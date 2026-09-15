# [H] Discourse: Public chat MessageBus broadcasts are not restricted to chat-eligible users

## Summary
Severity: High
Advisory: BIT-discourse-2026-44786
Aliases: CVE-2026-44786, GHSA-j7wq-rf5c-8783
Ecosystem: Bitnami
Published: 2026-06-16
Source: https://osv.dev/vulnerability/BIT-discourse-2026-44786
Type: osv

## Affected
- Bitnami: `discourse` — affected >=2026.4.0 <2026.4.1

## Details
Discourse is an open-source discussion platform. From versions 2026.1.0 to before 2026.1.4, 2026.3.0 to before 2026.3.1, and 2026.4.0 to before 2026.4.1, chat events for public category channels are published to MessageBus without permission scoping, so any MessageBus subscriber without chat enabled could receive chat message payloads in real time. This issue has been patched in versions 2026.1.4, 2026.3.1, 2026.4.1, and 2026.5.0.

## References
- https://github.com/discourse/discourse/security/advisories/GHSA-j7wq-rf5c-8783
- https://nvd.nist.gov/vuln/detail/CVE-2026-44786
