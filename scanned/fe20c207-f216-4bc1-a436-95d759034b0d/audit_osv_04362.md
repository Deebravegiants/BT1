# [H] Discourse moderators can edit themes via the API

## Summary
Severity: High
Advisory: BIT-discourse-2022-36068
Aliases: CVE-2022-36068, GHSA-6crr-3662-263q
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-discourse-2022-36068
Type: osv

## Affected
- Bitnami: `discourse` — affected >=0 <2.8.9

## Details
Discourse is an open source discussion platform. In versions prior to 2.8.9 on the `stable` branch and prior to 2.9.0.beta10 on the `beta` and `tests-passed` branches, a moderator can create new and edit existing themes by using the API when they should not be able to do so. The problem is patched in version 2.8.9 on the `stable` branch and version 2.9.0.beta10 on the `beta` and `tests-passed` branches. There are no known workarounds.

## References
- https://github.com/discourse/discourse/commit/ae1e536e83940d58f1c79b835c75c249121c46b6
- https://github.com/discourse/discourse/pull/18418
- https://github.com/discourse/discourse/security/advisories/GHSA-6crr-3662-263q
- https://nvd.nist.gov/vuln/detail/CVE-2022-36068
