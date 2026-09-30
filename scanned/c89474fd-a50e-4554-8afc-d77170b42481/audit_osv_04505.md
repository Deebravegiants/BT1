# [H] Discourse missing permission check for policy creation in discourse-policy

## Summary
Severity: High
Advisory: BIT-discourse-2026-29072
Aliases: CVE-2026-29072, GHSA-7ph8-vprq-4jrp
Ecosystem: Bitnami
Published: 2026-03-27
Source: https://osv.dev/vulnerability/BIT-discourse-2026-29072
Type: osv

## Affected
- Bitnami: `discourse` — affected >=2026.3.0 <2026.4.0

## Details
Discourse is an open-source discussion platform. Prior to versions 2026.3.0, 2026.2.1, and 2026.1.2, users who do not belong to the allowed policy creation groups can create functional policy acceptance widgets in posts under the right conditions. Versions 2026.3.0, 2026.2.1, and 2026.1.2 contain a patch. As a workaround, disable the discourse-policy plugin by disabling the `policy_enabled` site setting.

## References
- https://github.com/discourse/discourse/security/advisories/GHSA-7ph8-vprq-4jrp
- https://nvd.nist.gov/vuln/detail/CVE-2026-29072
