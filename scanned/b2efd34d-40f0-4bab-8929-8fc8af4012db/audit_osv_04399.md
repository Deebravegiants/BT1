# [M] Discourse vulnerable to exposure of number of topics recently created in private categories

## Summary
Severity: Medium
Advisory: BIT-discourse-2023-34250
Aliases: CVE-2023-34250, GHSA-q8m5-wmjr-3ppg
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-discourse-2023-34250
Type: osv

## Affected
- Bitnami: `discourse` — affected >=0 <3.0.4

## Details
Discourse is an open source discussion platform. Prior to version 3.0.4 of the `stable` branch and version 3.1.0.beta5 of the `beta` and `tests-passed` branches, an attacker could use the new topics dismissal endpoint to reveal the number of topics recently created (but not the actual content thereof) in categories they didn't have access to. This issue is patched in version 3.0.4 of the `stable` branch and version 3.1.0.beta5 of the `beta` and `tests-passed` branches. There are no known workarounds.

## References
- https://github.com/discourse/discourse/security/advisories/GHSA-q8m5-wmjr-3ppg
- https://nvd.nist.gov/vuln/detail/CVE-2023-34250
