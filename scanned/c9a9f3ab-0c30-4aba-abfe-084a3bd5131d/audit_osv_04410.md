# [M] Discourse DoS via remote theme assets

## Summary
Severity: Medium
Advisory: BIT-discourse-2023-41042
Aliases: CVE-2023-41042, GHSA-2fq5-x3mm-v254
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-discourse-2023-41042
Type: osv

## Affected
- Bitnami: `discourse` — affected >=0 <3.1.1

## Details
Discourse is an open-source discussion platform. Prior to version 3.1.1 of the `stable` branch and version 3.2.0.beta1 of the `beta` and `tests-passed` branches, importing a remote theme loads their assets into memory without enforcing limits for file size or number of files. The issue is patched in version 3.1.1 of the `stable` branch and version 3.2.0.beta1 of the `beta` and `tests-passed` branches. There are no known workarounds.

## References
- https://github.com/discourse/discourse/security/advisories/GHSA-2fq5-x3mm-v254
- https://nvd.nist.gov/vuln/detail/CVE-2023-41042
