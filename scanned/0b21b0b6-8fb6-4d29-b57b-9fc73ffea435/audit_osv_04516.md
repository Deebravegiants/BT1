# [M] Discourse: Cached outdated summaries can leak removed content

## Summary
Severity: Medium
Advisory: BIT-discourse-2026-32244
Aliases: CVE-2026-32244, GHSA-hjmg-2mww-vfvx
Ecosystem: Bitnami
Published: 2026-05-20
Source: https://osv.dev/vulnerability/BIT-discourse-2026-32244
Type: osv

## Affected
- Bitnami: `discourse` — affected >=2026.4.0 <2026.4.1

## Details
Discourse is an open-source discussion platform. In versions prior to 2026.1.4, 2026.3.1, 2026.4.1 and 2026.5.0, outdated cached AI summaries can leak removed content to anonymous and unprivileged users who cannot regenerate summaries. This issue has been fixed in versions 2026.1.4, 2026.3.1, 2026.4.1 and 2026.5.0. To work around this issue, restrict summary generation by tightening the allowed groups on the summarization Personas.

## References
- https://github.com/discourse/discourse/security/advisories/GHSA-hjmg-2mww-vfvx
- https://nvd.nist.gov/vuln/detail/CVE-2026-32244
