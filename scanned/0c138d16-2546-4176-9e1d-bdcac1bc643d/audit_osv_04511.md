# [M] Discourse prevents hidden profile data leak via user onebox

## Summary
Severity: Medium
Advisory: BIT-discourse-2026-32099
Aliases: CVE-2026-32099, GHSA-q83g-cj26-j4x5
Ecosystem: Bitnami
Published: 2026-03-27
Source: https://osv.dev/vulnerability/BIT-discourse-2026-32099
Type: osv

## Affected
- Bitnami: `discourse` — affected >=2026.3.0 <2026.3.0

## Details
Discourse is an open-source discussion platform. Prior to versions 2026.3.0, 2026.2.1, and 2026.1.2, when a user has `hide_profile` enabled, their bio, location, and website were still exposed through the user onebox preview. An authenticated user could request a onebox for a hidden user's profile URL and receive their hidden profile fields (bio, location, website) in the response. Versions 2026.3.0, 2026.2.1, and 2026.1.2 contain a patch. No known workarounds are available.

## References
- https://github.com/discourse/discourse/security/advisories/GHSA-q83g-cj26-j4x5
- https://nvd.nist.gov/vuln/detail/CVE-2026-32099
