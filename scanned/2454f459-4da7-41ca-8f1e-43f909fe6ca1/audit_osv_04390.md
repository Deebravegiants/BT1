# [M] Discourse vulnerable to multisite DoS by spamming backups

## Summary
Severity: Medium
Advisory: BIT-discourse-2023-28107
Aliases: CVE-2023-28107, GHSA-cp7c-fm4c-6xxx
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-discourse-2023-28107
Type: osv

## Affected
- Bitnami: `discourse` — affected >=0 <3.1.0

## Details
Discourse is an open-source discussion platform. Prior to version 3.0.2 of the `stable` branch and version 3.1.0.beta3 of the `beta` and `tests-passed` branches, a user logged as an administrator can request backups multiple times, which will eat up all the connections to the DB. If this is done on a site using multisite, then it can affect the whole cluster. The vulnerability is patched in version 3.0.2 of the `stable` branch and version 3.1.0.beta3 of the `beta` and `tests-passed` branches. There are no known workarounds.

## References
- https://github.com/discourse/discourse/commit/0bd64788d2b4680c04fbef76314a24884d65fed9
- https://github.com/discourse/discourse/commit/78a3efa7104eed6dd3ed7a06a71e2705337d9e61
- https://github.com/discourse/discourse/pull/20700
- https://github.com/discourse/discourse/pull/20701
- https://github.com/discourse/discourse/security/advisories/GHSA-cp7c-fm4c-6xxx
- https://nvd.nist.gov/vuln/detail/CVE-2023-28107
