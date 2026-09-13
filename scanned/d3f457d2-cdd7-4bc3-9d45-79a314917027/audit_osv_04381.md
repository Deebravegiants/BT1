# [M] Discourse restricted tag routes leak topic information

## Summary
Severity: Medium
Advisory: BIT-discourse-2023-23620
Aliases: CVE-2023-23620, GHSA-hvj9-g84x-5prx
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-discourse-2023-23620
Type: osv

## Affected
- Bitnami: `discourse` — affected >=0 <3.0.1

## Details
Discourse is an open-source discussion platform. Prior to version 3.0.1 on the `stable` branch and 3.1.0.beta2 on the `beta` and `tests-passed` branches, the contents of latest/top routes for restricted tags can be accessed by unauthorized users. This issue is patched in version 3.0.1 on the `stable` branch and 3.1.0.beta2 on the `beta` and `tests-passed` branches. There are no known workarounds.

## References
- https://github.com/discourse/discourse/commit/105fee978d73b0ec23ff814a09d1c0c9ace95164
- https://github.com/discourse/discourse/pull/20004
- https://github.com/discourse/discourse/security/advisories/GHSA-hvj9-g84x-5prx
- https://nvd.nist.gov/vuln/detail/CVE-2023-23620
