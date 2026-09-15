# [M] Discourse has race condition when adding users to a group DM

## Summary
Severity: Medium
Advisory: BIT-discourse-2025-24808
Aliases: CVE-2025-24808, GHSA-hfcx-qjw6-573r
Ecosystem: Bitnami
Published: 2025-03-28
Source: https://osv.dev/vulnerability/BIT-discourse-2025-24808
Type: osv

## Affected
- Bitnami: `discourse` — affected >=0 <3.4.0

## Details
Discourse is an open-source discussion platform. Prior to versions `3.3.4` on the `stable` branch and `3.4.0.beta5` on the `beta` branch, someone who is about to reach the limit of users in a group DM may send requests to add new users in parallel. The requests might all go through ignoring the limit due to a race condition. The patch in versions `3.3.4` and `3.4.0.beta5` uses the `lock` step in service to wrap part of the `add_users_to_channel` service inside a distributed lock/mutex in order to avoid the race condition.

## References
- https://github.com/discourse/discourse/commit/a16b2f224860f6678f89f5ffa012f0ede17e4095
- https://github.com/discourse/discourse/security/advisories/GHSA-hfcx-qjw6-573r
- https://nvd.nist.gov/vuln/detail/CVE-2025-24808
