# [C] Discourse SSRF vulnerability in Embedding

## Summary
Severity: Critical
Advisory: BIT-discourse-2023-47121
Aliases: CVE-2023-47121, GHSA-hp24-94qf-8cgc
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-discourse-2023-47121
Type: osv

## Affected
- Bitnami: `discourse` — affected >=0 <3.2.0

## Details
Discourse is an open source platform for community discussion. Prior to version 3.1.3 of the `stable` branch and version 3.2.0.beta3 of the `beta` and `tests-passed` branches, the embedding feature is susceptible to server side request forgery. The issue is patched in version 3.1.3 of the `stable` branch and version 3.2.0.beta3 of the `beta` and `tests-passed` branches. As a workaround, disable the Embedding feature.

## References
- https://github.com/discourse/discourse/commit/24cca10da731734af4e9748de99a508d586e59f1
- https://github.com/discourse/discourse/commit/5f20748e402223b265e6fee381472c14e2604da6
- https://github.com/discourse/discourse/security/advisories/GHSA-hp24-94qf-8cgc
- https://nvd.nist.gov/vuln/detail/CVE-2023-47121
