# [M] Discourse user profile location and website fields were not sufficiently length-limited

## Summary
Severity: Medium
Advisory: BIT-discourse-2022-39226
Aliases: CVE-2022-39226, GHSA-jw3q-xg5g-qjrw
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-discourse-2022-39226
Type: osv

## Affected
- Bitnami: `discourse` — affected >=0 <2.8.9

## Details
Discourse is an open source discussion platform. In versions prior to 2.8.9 on the `stable` branch and prior to 2.9.0.beta10 on the `beta` and `tests-passed` branches, a malicious actor can add large payloads of text into the Location and Website fields of a user profile, which causes issues for other users when loading that profile. A fix to limit the length of user input for these fields is included in version 2.8.9 on the `stable` branch and version 2.9.0.beta10 on the `beta` and `tests-passed` branches. There are no known workarounds.

## References
- https://github.com/discourse/discourse/commit/e69f7d2fd9c977dedbdb17f6813651e2a45bfb71
- https://github.com/discourse/discourse/pull/18302
- https://github.com/discourse/discourse/security/advisories/GHSA-jw3q-xg5g-qjrw
- https://nvd.nist.gov/vuln/detail/CVE-2022-39226
