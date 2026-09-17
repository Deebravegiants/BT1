# [M] Discourse has a subscription access bypass in its discourse-subscriptions plugin

## Summary
Severity: Medium
Advisory: BIT-discourse-2026-34154
Aliases: CVE-2026-34154, GHSA-pjgj-7mjq-6j7g
Ecosystem: Bitnami
Published: 2026-05-25
Source: https://osv.dev/vulnerability/BIT-discourse-2026-34154
Type: osv

## Affected
- Bitnami: `discourse` — affected >=2026.4.0 <2026.4.1

## Details
Discourse is an open-source discussion platform. In versions prior to 2026.1.4, 2026.3.1, 2026.4.1 and 2026.5.0, a vulnerability in the discourse-subscriptions plugin allows users to gain access to subscription-gated groups without completing payment. This issue has been fixed in versions 2026.1.4, 2026.3.1, 2026.4.1 and 2026.5.0.

## References
- https://github.com/discourse/discourse/security/advisories/GHSA-pjgj-7mjq-6j7g
- https://nvd.nist.gov/vuln/detail/CVE-2026-34154
