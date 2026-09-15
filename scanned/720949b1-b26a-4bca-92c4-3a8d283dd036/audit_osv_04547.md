# [M] Discourse: GroupPostSerializer leaks hidden full names through reaction post association

## Summary
Severity: Medium
Advisory: BIT-discourse-2026-44782
Aliases: CVE-2026-44782, GHSA-h3mq-9r6w-h33j
Ecosystem: Bitnami
Published: 2026-06-16
Source: https://osv.dev/vulnerability/BIT-discourse-2026-44782
Type: osv

## Affected
- Bitnami: `discourse` — affected >=2026.4.0 <2026.4.1

## Details
Discourse is an open-source discussion platform. From versions 2026.1.0 to before 2026.1.4, 2026.3.0 to before 2026.3.1, and 2026.4.0 to before 2026.4.1, GroupPostSerializer declared include_user_long_name? as the predicate for its :name attribute, but AMS looks for include_name?. The misnamed predicate was never called, so object.user.name was always serialized regardless of SiteSetting.enable_names. This issue has been patched in versions 2026.1.4, 2026.3.1, 2026.4.1, and 2026.5.0.

## References
- https://github.com/discourse/discourse/security/advisories/GHSA-h3mq-9r6w-h33j
- https://nvd.nist.gov/vuln/detail/CVE-2026-44782
