# [M] Discourse: Private event sample invitees are serialized to non-invited event viewers

## Summary
Severity: Medium
Advisory: BIT-discourse-2026-45780
Aliases: CVE-2026-45780, GHSA-22v7-6wgj-g9f7
Ecosystem: Bitnami
Published: 2026-07-15
Source: https://osv.dev/vulnerability/BIT-discourse-2026-45780
Type: osv

## Affected
- Bitnami: `discourse` — affected >=2026.5.0 <2026.5.1

## Details
Discourse is an open-source discussion platform. Prior to 2026.6.0, 2026.5.1, 2026.4.2, and 2026.1.5, EventSerializer could expose invited group names, sample invitees, and attendance statistics to users who could view the topic but were not entitled to view the private event invitee list. This issue is fixed in versions 2026.6.0, 2026.5.1, 2026.4.2, and 2026.1.5.

## References
- https://github.com/discourse/discourse/commit/37969503f20369eb1712b7b88daedcfb4f63f5f1
- https://github.com/discourse/discourse/commit/4d46638041b5f3d1e1f7f6f6f19c1df3bd65a586
- https://github.com/discourse/discourse/commit/6457ab71f36a2d1440fe96af0a2593897844b023
- https://github.com/discourse/discourse/commit/7deb4b6963442569357b41e61febe37594e5e730
- https://github.com/discourse/discourse/releases/tag/v2026.1.5
- https://github.com/discourse/discourse/releases/tag/v2026.4.2
- https://github.com/discourse/discourse/releases/tag/v2026.5.1
- https://github.com/discourse/discourse/releases/tag/v2026.6.0
- https://github.com/discourse/discourse/security/advisories/GHSA-22v7-6wgj-g9f7
- https://nvd.nist.gov/vuln/detail/CVE-2026-45780
