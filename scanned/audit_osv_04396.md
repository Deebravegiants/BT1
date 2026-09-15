# [M] Discourse's general category permissions could be set back to default

## Summary
Severity: Medium
Advisory: BIT-discourse-2023-31142
Aliases: CVE-2023-31142, GHSA-286w-97m2-78x2
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-discourse-2023-31142
Type: osv

## Affected
- Bitnami: `discourse` — affected >=0 <3.0.4

## Details
Discourse is an open source discussion platform. Prior to version 3.0.4 of the `stable` branch and version 3.1.0.beta5 of the `beta` and `tests-passed` branches, if a site has modified their general category permissions, they could be set back to the default. This issue is patched in version 3.0.4 of the `stable` branch and version 3.1.0.beta5 of the `beta` and `tests-passed` branches. A workaround, only if you are modifying the general category permissions, is to use a new category for the same purpose.

## References
- https://github.com/discourse/discourse/security/advisories/GHSA-286w-97m2-78x2
- https://nvd.nist.gov/vuln/detail/CVE-2023-31142
