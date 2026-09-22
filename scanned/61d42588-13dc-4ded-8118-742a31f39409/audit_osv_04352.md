# [M] Discourse vulnerable to bypass of post max_length using HTML comments

## Summary
Severity: Medium
Advisory: BIT-discourse-2022-23549
Aliases: CVE-2022-23549, GHSA-p47g-v5wr-p4xp
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-discourse-2022-23549
Type: osv

## Affected
- Bitnami: `discourse` — affected >=0 <2.8.14

## Details
Discourse is an option source discussion platform. Prior to version 2.8.14 on the `stable` branch and version 2.9.0.beta16 on the `beta` and `tests-passed` branches, users can create posts with raw body longer than the `max_length` site setting by including html comments that are not counted toward the character limit. This issue is patched in versions 2.8.14 and 2.9.0.beta16. There are no known workarounds.

## References
- https://github.com/discourse/discourse/commit/bf6b08670a927cc80bb090b7a2e710b4b554e6a8
- https://github.com/discourse/discourse/security/advisories/GHSA-p47g-v5wr-p4xp
- https://nvd.nist.gov/vuln/detail/CVE-2022-23549
