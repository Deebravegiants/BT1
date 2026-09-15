# [M] Discourse: Staged user custom fields are exposed on public invite pages

## Summary
Severity: Medium
Advisory: BIT-discourse-2026-34947
Aliases: CVE-2026-34947, GHSA-4rcw-wq9x-54qw
Ecosystem: Bitnami
Published: 2026-04-08
Source: https://osv.dev/vulnerability/BIT-discourse-2026-34947
Type: osv

## Affected
- Bitnami: `discourse` — affected >=2026.2.0 <2026.2.2

## Details
Discourse is an open-source discussion platform. From versions 2026.1.0 to before 2026.1.3,and 2026.2.0 to before 2026.2.2, staged user custom fields and username are exposed on public invite pages without email verification. This issue has been patched in versions 2026.1.3 and 2026.2.2.

## References
- https://github.com/discourse/discourse/security/advisories/GHSA-4rcw-wq9x-54qw
- https://nvd.nist.gov/vuln/detail/CVE-2026-34947
