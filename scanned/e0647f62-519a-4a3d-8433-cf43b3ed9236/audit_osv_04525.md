# [M] Discourse: Vulnerability in discourse-subscriptions plugin allowing users to self-grant to higher tier subscriptions

## Summary
Severity: Medium
Advisory: BIT-discourse-2026-33074
Aliases: CVE-2026-33074, GHSA-9vg5-mp49-xghh
Ecosystem: Bitnami
Published: 2026-04-07
Source: https://osv.dev/vulnerability/BIT-discourse-2026-33074
Type: osv

## Affected
- Bitnami: `discourse` — affected >=2026.2.0 <2026.2.2

## Details
Discourse is an open-source discussion platform. From versions 2026.1.0 to before 2026.1.3, and 2026.2.0 to before 2026.2.2, a user may be able to purchase a lower tier subscription but grant themselves the benefits that comes along with a higher tier subscription. This issue has been patched in versions 2026.1.3, 2026.2.2, and 2026.3.0.

## References
- https://github.com/discourse/discourse/commit/c34f2aac8dcd1ae2886fa84256f607bc003f9d80
- https://github.com/discourse/discourse/security/advisories/GHSA-9vg5-mp49-xghh
- https://nvd.nist.gov/vuln/detail/CVE-2026-33074
