# [H] Discourse: Remote code execution via pdf uploads

## Summary
Severity: High
Advisory: BIT-discourse-2026-55420
Aliases: CVE-2026-55420, GHSA-7wq5-jgww-5rw3
Ecosystem: Bitnami
Published: 2026-07-14
Source: https://osv.dev/vulnerability/BIT-discourse-2026-55420
Type: osv

## Affected
- Bitnami: `discourse` — affected >=2026.6.0 <2026.7.0

## Details
Discourse is an open-source discussion platform. Prior to 2026.6.0, 2026.5.1, 2026.4.2, and 2026.1.5, under certain non-default configurations, processing of PDF uploads could be exploited to obtain RCE on the server. This issue is patched in 2026.6.0, 2026.5.1, 2026.4.2, and 2026.1.5.

## References
- https://github.com/discourse/discourse/commit/ca5a7e06167561928556afa2f237d67e459c6914
- https://github.com/discourse/discourse/releases/tag/v2026.1.5
- https://github.com/discourse/discourse/releases/tag/v2026.4.2
- https://github.com/discourse/discourse/releases/tag/v2026.5.1
- https://github.com/discourse/discourse/releases/tag/v2026.6.0
- https://github.com/discourse/discourse/security/advisories/GHSA-7wq5-jgww-5rw3
- https://nvd.nist.gov/vuln/detail/CVE-2026-55420
