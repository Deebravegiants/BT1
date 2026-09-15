# [M] Discourse vulnerable to exposure of user post counts per topic to unauthorized users

## Summary
Severity: Medium
Advisory: BIT-discourse-2023-22453
Aliases: CVE-2023-22453, GHSA-xx97-6494-p2rv
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-discourse-2023-22453
Type: osv

## Affected
- Bitnami: `discourse` — affected >=0 <2.8.14

## Details
Discourse is an option source discussion platform. Prior to version 2.8.14 on the `stable` branch and version 3.0.0.beta16 on the `beta` and `tests-passed` branches, the number of times a user posted in an arbitrary topic is exposed to unauthorized users through the `/u/username.json` endpoint. The issue is patched in version 2.8.14 and 3.0.0.beta16. There is no known workaround.

## References
- https://github.com/discourse/discourse/commit/cbcf8a064b4889a19c991641e09c399bfa1ef2ad
- https://github.com/discourse/discourse/security/advisories/GHSA-xx97-6494-p2rv
- https://nvd.nist.gov/vuln/detail/CVE-2023-22453
