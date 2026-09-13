# [M] Discourse discloses restricted post-action counts to non-privileged users

## Summary
Severity: Medium
Advisory: BIT-discourse-2026-27936
Aliases: CVE-2026-27936, GHSA-v9r3-p863-6f25
Ecosystem: Bitnami
Published: 2026-03-27
Source: https://osv.dev/vulnerability/BIT-discourse-2026-27936
Type: osv

## Affected
- Bitnami: `discourse` — affected >=2026.3.0 <2026.4.0

## Details
Discourse is an open-source discussion platform. Prior to versions 2026.3.0, 2026.2.1, and 2026.1.2, a restriction bypass allows restricted post action counts to be disclosed to non-privileged users through a carefully crafted request. Versions 2026.3.0, 2026.2.1, and 2026.1.2 contain a patch. No known workarounds are available.

## References
- https://github.com/discourse/discourse/security/advisories/GHSA-v9r3-p863-6f25
- https://nvd.nist.gov/vuln/detail/CVE-2026-27936
