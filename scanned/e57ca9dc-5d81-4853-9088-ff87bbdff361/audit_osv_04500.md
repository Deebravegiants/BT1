# [M] Discourse leaks private topic metadata to non-authorized users

## Summary
Severity: Medium
Advisory: BIT-discourse-2026-27935
Aliases: CVE-2026-27935, GHSA-wxqr-r4wv-cw76
Ecosystem: Bitnami
Published: 2026-03-27
Source: https://osv.dev/vulnerability/BIT-discourse-2026-27935
Type: osv

## Affected
- Bitnami: `discourse` — affected >=2026.3.0 <2026.4.0

## Details
Discourse is an open-source discussion platform. Versions prior to 2026.3.0, 2026.2.1, and 2026.1.2 have a vulnerability in an API endpoint that discloses private topic metadata of admin users to moderator users even if the moderators do not have access to the private topics. Versions 2026.3.0, 2026.2.1, and 2026.1.2 contain a patch. No known workarounds are available.

## References
- https://github.com/discourse/discourse/commit/c0f6e9a903800de0dda65c114418ae703d8a51fc
- https://github.com/discourse/discourse/commit/d8dbb4cb189cded8c9e8b3ada859fc0db3f41897
- https://github.com/discourse/discourse/commit/f37e4fdf8391e4a54f1885a3a5514d390eb28bab
- https://github.com/discourse/discourse/security/advisories/GHSA-wxqr-r4wv-cw76
- https://nvd.nist.gov/vuln/detail/CVE-2026-27935
