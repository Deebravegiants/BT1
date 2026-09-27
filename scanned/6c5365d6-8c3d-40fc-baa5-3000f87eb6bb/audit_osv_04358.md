# [M] Banner topic data is exposed on login-required Discourse sites

## Summary
Severity: Medium
Advisory: BIT-discourse-2022-31060
Aliases: CVE-2022-31060, GHSA-5f4f-35fx-gqhq
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-discourse-2022-31060
Type: osv

## Affected
- Bitnami: `discourse` — affected >=0 <2.8.4

## Details
Discourse is an open-source discussion platform. Prior to version 2.8.4 in the `stable` branch and version `2.9.0.beta5` in the `beta` and `tests-passed` branches, banner topic data is exposed on login-required sites. This issue is patched in version 2.8.4 in the `stable` branch and version `2.9.0.beta5` in the `beta` and `tests-passed` branches of Discourse. As a workaround, one may disable banners.

## References
- https://github.com/discourse/discourse/commit/ae6a9079436fb9b20fd051d25fb6d8027f0ec59a
- https://github.com/discourse/discourse/pull/17071
- https://github.com/discourse/discourse/security/advisories/GHSA-5f4f-35fx-gqhq
- https://nvd.nist.gov/vuln/detail/CVE-2022-31060
