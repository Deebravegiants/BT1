# [M] Invite bypasses user approval in Discourse

## Summary
Severity: Medium
Advisory: BIT-discourse-2022-31025
Aliases: CVE-2022-31025, GHSA-x7jh-mx5q-6f9q
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-discourse-2022-31025
Type: osv

## Affected
- Bitnami: `discourse` — affected >=0 <2.8.4

## Details
Discourse is an open source platform for community discussion. Prior to version 2.8.4 on the `stable` branch and 2.9.0 on the `beta` and `tests-passed` branches, inviting users on sites that use single sign-on could bypass the `must_approve_users` check and invites by staff are always approved automatically. The issue is patched in Discourse version 2.8.4 on the `stable` branch and version `2.9.0.beta5` on the `beta` and `tests-passed` branches. As a workaround, disable invites or increase `min_trust_level_to_allow_invite` to reduce the attack surface to more trusted users.

## References
- https://github.com/discourse/discourse/commit/0fa0094531efc82d9371f90a02aa804b176d59cf
- https://github.com/discourse/discourse/commit/7c4e2d33fa4b922354c177ffc880a2f2701a91f9
- https://github.com/discourse/discourse/pull/16974
- https://github.com/discourse/discourse/pull/16984
- https://github.com/discourse/discourse/security/advisories/GHSA-x7jh-mx5q-6f9q
- https://nvd.nist.gov/vuln/detail/CVE-2022-31025
