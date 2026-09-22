# [H] Discourse vulnerable to unlimited mentioned users in message serializer

## Summary
Severity: High
Advisory: BIT-discourse-2023-48297
Aliases: CVE-2023-48297, GHSA-hf2v-r5xm-8p37
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-discourse-2023-48297
Type: osv

## Affected
- Bitnami: `discourse` — affected >=0 <3.1.4

## Details
Discourse is a platform for community discussion. The message serializer uses the full list of expanded chat mentions (@all and @here) which can lead to a very long array of users. This issue was patched in versions 3.1.4 and beta 3.2.0.beta5.

## References
- https://github.com/discourse/discourse/security/advisories/GHSA-hf2v-r5xm-8p37
- https://nvd.nist.gov/vuln/detail/CVE-2023-48297
