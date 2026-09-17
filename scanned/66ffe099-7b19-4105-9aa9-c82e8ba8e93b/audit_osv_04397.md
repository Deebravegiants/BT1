# [M] Discourse Topic Creation Page Allows iFrame Tag without Restrictions

## Summary
Severity: Medium
Advisory: BIT-discourse-2023-32061
Aliases: CVE-2023-32061, GHSA-prx4-49m8-874g
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-discourse-2023-32061
Type: osv

## Affected
- Bitnami: `discourse` — affected >=0 <3.0.4

## Details
Discourse is an open source discussion platform. Prior to version 3.0.4 of the `stable` branch and version 3.1.0.beta5 of the `beta` and `tests-passed` branches, the lack of restrictions on the iFrame tag makes it easy for an attacker to exploit the vulnerability and hide subsequent comments from other users. This issue is patched in version 3.0.4 of the `stable` branch and version 3.1.0.beta5 of the `beta` and `tests-passed` branches. There are no known workarounds.

## References
- https://github.com/discourse/discourse/security/advisories/GHSA-prx4-49m8-874g
- https://nvd.nist.gov/vuln/detail/CVE-2023-32061
