# [M] Discourse: Bot debug endpoints disclose whisper translation audit logs

## Summary
Severity: Medium
Advisory: BIT-discourse-2026-44779
Aliases: CVE-2026-44779, GHSA-x6mr-wjq6-495j
Ecosystem: Bitnami
Published: 2026-06-16
Source: https://osv.dev/vulnerability/BIT-discourse-2026-44779
Type: osv

## Affected
- Bitnami: `discourse` — affected >=2026.4.0 <2026.4.1

## Details
Discourse is an open-source discussion platform. From versions 2026.1.0 to before 2026.1.4, 2026.3.0 to before 2026.3.1, and 2026.4.0 to before 2026.4.1, bot debug endpoints disclose whisper translation audit logs. This issue has been patched in versions 2026.1.4, 2026.3.1, 2026.4.1, and 2026.5.0.

## References
- https://github.com/discourse/discourse/security/advisories/GHSA-x6mr-wjq6-495j
- https://nvd.nist.gov/vuln/detail/CVE-2026-44779
