# [M] Discourse missing authorization checks for suspending admins/moderators

## Summary
Severity: Medium
Advisory: BIT-discourse-2024-36113
Aliases: CVE-2024-36113, GHSA-3w3f-76p7-3c4g
Ecosystem: Bitnami
Published: 2024-07-09
Source: https://osv.dev/vulnerability/BIT-discourse-2024-36113
Type: osv

## Affected
- Bitnami: `discourse` — affected >=0 <3.2.3

## Details
Discourse is an open-source discussion platform. Prior to version 3.2.3 on the `stable` branch, version 3.3.0.beta3 on the `beta` branch, and version 3.3.0.beta4-dev on the `tests-passed` branch, a rogue staff user could suspend other staff users preventing them from logging in to the site. The issue is patched in version 3.2.3 on the `stable` branch, version 3.3.0.beta3 on the `beta` branch, and version 3.3.0.beta4-dev on the `tests-passed` branch. No known workarounds are available.

## References
- https://github.com/discourse/discourse/commit/8470546f59b04bd82ce9b711406758fd5439936d
- https://github.com/discourse/discourse/commit/9c4a5f39d3ad351410a1453ff5e5f7ffce17cd7e
- https://github.com/discourse/discourse/security/advisories/GHSA-3w3f-76p7-3c4g
- https://nvd.nist.gov/vuln/detail/CVE-2024-36113
