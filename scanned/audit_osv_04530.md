# [M] Discourse filters whisper posts from private-posts feed

## Summary
Severity: Medium
Advisory: BIT-discourse-2026-33355
Aliases: CVE-2026-33355, GHSA-g4v5-6gfp-3hjq
Ecosystem: Bitnami
Published: 2026-03-27
Source: https://osv.dev/vulnerability/BIT-discourse-2026-33355
Type: osv

## Affected
- Bitnami: `discourse` — affected >=2026.3.0 <2026.3.0

## Details
Discourse is an open-source discussion platform. Prior to versions 2026.3.0, 2026.2.1, and 2026.1.2, the `/private-posts` endpoint did not apply post-type visibility filtering, allowing regular PM participants to see whisper posts in PM topics they had access to. Versions 2026.3.0, 2026.2.1, and 2026.1.2 contain a patch. No known workarounds are available.

## References
- https://github.com/discourse/discourse/commit/84e5865a279716c6866e8c0648d1d8b42320603c
- https://github.com/discourse/discourse/commit/d25b8ee9ee182dbb34e92b34e39878ce4d59bcdc
- https://github.com/discourse/discourse/commit/d2f317271ad7638f1e2791905472ebd9370946d1
- https://github.com/discourse/discourse/security/advisories/GHSA-g4v5-6gfp-3hjq
- https://nvd.nist.gov/vuln/detail/CVE-2026-33355
