# [M] Discourse's restricted tag information visible to unauthenticated users

## Summary
Severity: Medium
Advisory: BIT-discourse-2023-38685
Aliases: CVE-2023-38685, GHSA-wx6x-q4gp-mgv5
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-discourse-2023-38685
Type: osv

## Affected
- Bitnami: `discourse` — affected >=0 <3.0.6

## Details
Discourse is an open source discussion platform. Prior to version 3.0.6 of the `stable` branch and version 3.1.0.beta7 of the `beta` and `tests-passed` branches, information about restricted-visibility topic tags could be obtained by unauthorized users. The issue is patched in version 3.0.6 of the `stable` branch and version 3.1.0.beta7 of the `beta` and `tests-passed` branches.

## References
- https://github.com/discourse/discourse/commit/073661142369a0a66c25775cc3870582a679ef8b
- https://github.com/discourse/discourse/security/advisories/GHSA-wx6x-q4gp-mgv5
- https://nvd.nist.gov/vuln/detail/CVE-2023-38685
