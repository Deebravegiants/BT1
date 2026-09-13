# [M] Discourse DoS via SvgSprite cache

## Summary
Severity: Medium
Advisory: BIT-discourse-2023-41043
Aliases: CVE-2023-41043, GHSA-28hh-h5xw-xgvx
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-discourse-2023-41043
Type: osv

## Affected
- Bitnami: `discourse` — affected >=0 <3.1.1

## Details
Discourse is an open-source discussion platform. Prior to version 3.1.1 of the `stable` branch and version 3.2.0.beta1 of the `beta` and `tests-passed` branches, a malicious admin could create extremely large icons sprites, which would then be cached in each server process. This may cause server processes to be killed and lead to downtime. The issue is patched in version 3.1.1 of the `stable` branch and version 3.2.0.beta1 of the `beta` and `tests-passed` branches. This is only a concern for multisite installations. No action is required when the admins are trusted.

## References
- https://github.com/discourse/discourse/security/advisories/GHSA-28hh-h5xw-xgvx
- https://nvd.nist.gov/vuln/detail/CVE-2023-41043
