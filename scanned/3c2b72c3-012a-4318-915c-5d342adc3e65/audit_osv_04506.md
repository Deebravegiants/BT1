# [M] Discourse has moderator privilege escalation via arbitrary post_id in suspend/silence endpoint

## Summary
Severity: Medium
Advisory: BIT-discourse-2026-30888
Aliases: CVE-2026-30888, GHSA-jj9p-p7m6-jq96
Ecosystem: Bitnami
Published: 2026-03-27
Source: https://osv.dev/vulnerability/BIT-discourse-2026-30888
Type: osv

## Affected
- Bitnami: `discourse` — affected >=0 <2026.3.0

## Details
Discourse is an open-source discussion platform. Versions prior to 2026.3.0, 2026.2.1, and 2026.1.2 allow a moderator to edit site policy documents (ToS, guidelines, privacy policy) that they are explicitly prohibited from modifying. Versions 2026.3.0, 2026.2.1, and 2026.1.2 contain a patch. No known workarounds are available.

## References
- https://github.com/discourse/discourse/security/advisories/GHSA-jj9p-p7m6-jq96
- https://nvd.nist.gov/vuln/detail/CVE-2026-30888
