# [M] Discourse vulnerable to DoS via post edit reason

## Summary
Severity: Medium
Advisory: BIT-discourse-2023-37906
Aliases: CVE-2023-37906, GHSA-pjv6-47x6-mx7c
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-discourse-2023-37906
Type: osv

## Affected
- Bitnami: `discourse` — affected >=0 <3.0.6

## Details
Discourse is an open source discussion platform. Prior to version 3.0.6 of the `stable` branch and version 3.1.0.beta7 of the `beta` and `tests-passed` branches, a malicious user can edit a post in a topic and cause a DoS with a carefully crafted edit reason. The issue is patched in version 3.0.6 of the `stable` branch and version 3.1.0.beta7 of the `beta` and `tests-passed` branches. There are no known workarounds for this vulnerability.

## References
- https://github.com/discourse/discourse/commit/dcc825bda505a344eda403a1b8733f30e784034a
- https://github.com/discourse/discourse/security/advisories/GHSA-pjv6-47x6-mx7c
- https://nvd.nist.gov/vuln/detail/CVE-2023-37906
