# [M] Discourse membership requests lack character limit

## Summary
Severity: Medium
Advisory: BIT-discourse-2023-23616
Aliases: CVE-2023-23616, GHSA-6xff-p329-9pgf
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-discourse-2023-23616
Type: osv

## Affected
- Bitnami: `discourse` — affected >=0 <3.0.1

## Details
Discourse is an open-source discussion platform. Prior to version 3.0.1 on the `stable` branch and 3.1.0.beta2 on the `beta` and `tests-passed` branches, when submitting a membership request, there is no character limit for the reason provided with the request. This could potentially allow a user to flood the database with a large amount of data. However it is unlikely this could be used as part of a DoS attack, as the paths reading back the reasons are only available to administrators. Starting in version 3.0.1 on the `stable` branch and 3.1.0.beta2 on the `beta` and `tests-passed` branches, a limit of 280 characters has been introduced for membership requests.

## References
- https://github.com/discourse/discourse/commit/3e0cc4a5d9ef44ad902f6985d046ebb32f0a14ee
- https://github.com/discourse/discourse/commit/d5745d34c20c31a221039d8913f33064433003ea
- https://github.com/discourse/discourse/pull/19993
- https://github.com/discourse/discourse/security/advisories/GHSA-6xff-p329-9pgf
- https://nvd.nist.gov/vuln/detail/CVE-2023-23616
