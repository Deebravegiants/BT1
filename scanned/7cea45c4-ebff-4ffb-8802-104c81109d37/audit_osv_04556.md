# [H] Discourse: Secure uploads exposed by hotlinked image copying

## Summary
Severity: High
Advisory: BIT-discourse-2026-45788
Aliases: CVE-2026-45788, GHSA-3876-w96v-8v38
Ecosystem: Bitnami
Published: 2026-07-15
Source: https://osv.dev/vulnerability/BIT-discourse-2026-45788
Type: osv

## Affected
- Bitnami: `discourse` — affected >=2026.5.0 <2026.5.1

## Details
Discourse is an open-source discussion platform. Prior to 2026.6.0, 2026.5.1, 2026.4.2, and 2026.1.5, secure uploads could be exposed by pull_hotlinked_images when an attacker knew the secured upload URL and the secure_uploads site setting was enabled. This issue is fixed in versions 2026.6.0, 2026.5.1, 2026.4.2, and 2026.1.5.

## References
- https://github.com/discourse/discourse/commit/5807c426880eadf248006e851604fc9284327ce5
- https://github.com/discourse/discourse/commit/8b4a959b251a856a9c911fb9f2ac34fbc31a7471
- https://github.com/discourse/discourse/commit/eff53af26367ae0dcb3a426954d233e8c7449f95
- https://github.com/discourse/discourse/commit/fa74e0dec7341a858ab83a1977fa52629bced1aa
- https://github.com/discourse/discourse/releases/tag/v2026.1.5
- https://github.com/discourse/discourse/releases/tag/v2026.4.2
- https://github.com/discourse/discourse/releases/tag/v2026.5.1
- https://github.com/discourse/discourse/releases/tag/v2026.6.0
- https://github.com/discourse/discourse/security/advisories/GHSA-3876-w96v-8v38
- https://nvd.nist.gov/vuln/detail/CVE-2026-45788
