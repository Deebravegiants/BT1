# [M] Discourse tags with no visibility are leaking into og:article:tag

## Summary
Severity: Medium
Advisory: BIT-discourse-2023-25819
Aliases: CVE-2023-25819, GHSA-xx2h-mwm7-hq6q
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-discourse-2023-25819
Type: osv

## Affected
- Bitnami: `discourse` — affected >=0 <3.1.0

## Details
Discourse is an open source platform for community discussion. Tags that are normally private are showing in metadata. This affects any site running the `tests-passed` or `beta` branches >= 3.1.0.beta2. The issue is patched in the latest `beta` and `tests-passed` version of Discourse.

## References
- https://github.com/discourse/discourse/commit/a9f2c6db64e7d78b8e0f55e7bd77c5fe3459b831
- https://github.com/discourse/discourse/security/advisories/GHSA-xx2h-mwm7-hq6q
- https://nvd.nist.gov/vuln/detail/CVE-2023-25819
