# [M] Discourse user can create Zendesk tickets even when it does not have access to topic

## Summary
Severity: Medium
Advisory: BIT-discourse-2026-33291
Aliases: CVE-2026-33291, GHSA-p26h-jqr4-r6j7
Ecosystem: Bitnami
Published: 2026-03-27
Source: https://osv.dev/vulnerability/BIT-discourse-2026-33291
Type: osv

## Affected
- Bitnami: `discourse` — affected >=2026.3.0 <2026.3.0

## Details
Discourse is an open-source discussion platform. Prior to versions 2026.3.0, 2026.2.1, and 2026.1.2, moderators can create Zendesk tickets for topics they do not have access to view. This affects all forums that use the Zendesk plugin. Versions 2026.3.0, 2026.2.1, and 2026.1.2 contain a patch. No known workarounds are available.

## References
- https://github.com/discourse/discourse/security/advisories/GHSA-p26h-jqr4-r6j7
- https://nvd.nist.gov/vuln/detail/CVE-2026-33291
