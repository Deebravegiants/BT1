# [M] Any authenticated Discourse user can create an unlisted topic

## Summary
Severity: Medium
Advisory: BIT-discourse-2022-46159
Aliases: CVE-2022-46159, GHSA-qf99-xpx6-hgxp
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-discourse-2022-46159
Type: osv

## Affected
- Bitnami: `discourse` — affected >=0 <2.8.14

## Details
Discourse is an open-source discussion platform. In version 2.8.13 and prior on the `stable` branch and version 2.9.0.beta14 and prior on the `beta` and `tests-passed` branches, any authenticated user can create an unlisted topic. These topics, which are not readily available to other users, can take up unnecessary site resources. A patch for this issue is available in the `main` branch of Discourse. There are no known workarounds available.

## References
- https://github.com/discourse/discourse/commit/0ce38bd7bce862db251b882613ab7053ca777382
- https://github.com/discourse/discourse/security/advisories/GHSA-qf99-xpx6-hgxp
- https://nvd.nist.gov/vuln/detail/CVE-2022-46159
