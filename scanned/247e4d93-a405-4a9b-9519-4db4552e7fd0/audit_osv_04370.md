# [M] Discourse users can see notifications for topics they no longer have access to

## Summary
Severity: Medium
Advisory: BIT-discourse-2022-41944
Aliases: CVE-2022-41944, GHSA-354r-jpj5-53c2
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-discourse-2022-41944
Type: osv

## Affected
- Bitnami: `discourse` — affected >=0 <2.8.12

## Details
Discourse is an open-source discussion platform. In stable versions prior to 2.8.12 and beta or tests-passed versions prior to 2.9.0.beta.13, under certain conditions, a user can see notifications for topics they no longer have access to. If there is sensitive information in the topic title, it will therefore have been exposed. This issue is patched in stable version 2.8.12, beta version 2.9.0.beta13, and tests-passed version 2.9.0.beta13. There are no workarounds available.

## References
- https://github.com/discourse/discourse/commit/c6ee28ec756436cc9ce154dd2c8e4c441f92f693
- https://github.com/discourse/discourse/security/advisories/GHSA-354r-jpj5-53c2
- https://nvd.nist.gov/vuln/detail/CVE-2022-41944
