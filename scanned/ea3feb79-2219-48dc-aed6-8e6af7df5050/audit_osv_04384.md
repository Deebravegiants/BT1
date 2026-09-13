# [M] Discourse's exclude_tags param could leak which topics had a specific hidden tag

## Summary
Severity: Medium
Advisory: BIT-discourse-2023-23624
Aliases: CVE-2023-23624, GHSA-qgj5-g5vf-fm7q
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-discourse-2023-23624
Type: osv

## Affected
- Bitnami: `discourse` — affected >=0 <3.0.1

## Details
Discourse is an open-source discussion platform. Prior to version 3.0.1 on the `stable` branch and version 3.1.0.beta2 on the `beta` and `tests-passed` branches, someone can use the `exclude_tag param` to filter out topics and deduce which ones were using a specific hidden tag. This affects any Discourse site using hidden tags in public categories. This issue is patched in version 3.0.1 on the `stable` branch and version 3.1.0.beta2 on the `beta` and `tests-passed` branches. As a workaround, secure any categories that are using hidden tags, change any existing hidden tags to not include private data, or remove any hidden tags currently in use.

## References
- https://github.com/discourse/discourse/commit/f55e0fe7910149c431861c18ce407d1be0d6091a
- https://github.com/discourse/discourse/pull/20006
- https://github.com/discourse/discourse/security/advisories/GHSA-qgj5-g5vf-fm7q
- https://nvd.nist.gov/vuln/detail/CVE-2023-23624
