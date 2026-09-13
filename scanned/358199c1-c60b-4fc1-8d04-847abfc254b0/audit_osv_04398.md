# [M] Discourse's canonical url not being used for topic embeddings

## Summary
Severity: Medium
Advisory: BIT-discourse-2023-32301
Aliases: CVE-2023-32301, GHSA-p2jx-m2j5-hqh4
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-discourse-2023-32301
Type: osv

## Affected
- Bitnami: `discourse` — affected >=0 <3.0.4

## Details
Discourse is an open source discussion platform. Prior to version 3.0.4 of the `stable` branch and version 3.1.0.beta5 of the `beta` and `tests-passed` branches, multiple duplicate topics could be created if topic embedding is enabled. This issue is patched in version 3.0.4 of the `stable` branch and version 3.1.0.beta5 of the `beta` and `tests-passed` branches. As a workaround, disable topic embedding if it has been enabled.

## References
- https://github.com/discourse/discourse/security/advisories/GHSA-p2jx-m2j5-hqh4
- https://nvd.nist.gov/vuln/detail/CVE-2023-32301
