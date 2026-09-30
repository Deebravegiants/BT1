# [M] Discourse: Forged AWS SNS bounce notifications can disable a targeted user's email (missing TopicArn binding)

## Summary
Severity: Medium
Advisory: BIT-discourse-2026-53961
Aliases: CVE-2026-53961, GHSA-8f9m-v436-wr3x
Ecosystem: Bitnami
Published: 2026-07-15
Source: https://osv.dev/vulnerability/BIT-discourse-2026-53961
Type: osv

## Affected
- Bitnami: `discourse` — affected >=2026.5.0 <2026.5.1

## Details
Discourse is an open-source discussion platform. Prior to 2026.6.0, 2026.5.1, 2026.4.2, and 2026.1.5, the AWS SES bounce webhook at POST /webhooks/aws verified that SNS messages were signed by Amazon but did not bind them to trusted TopicArn values, allowing any AWS account holder to publish validly signed forged Bounce notifications that revoke a targeted user email. This issue is fixed in versions 2026.6.0, 2026.5.1, 2026.4.2, and 2026.1.5.

## References
- https://github.com/discourse/discourse/commit/3a3d315a85ef3c6aabfc7e7bb38702059784f06b
- https://github.com/discourse/discourse/commit/61f12e13aa1b760f81d5ff60f12e3a7e77434b94
- https://github.com/discourse/discourse/commit/958f0cd831d65a49ec75f05343ca2c167679f0ea
- https://github.com/discourse/discourse/commit/aea35190791261bab258ebab05da279e78cdd0e6
- https://github.com/discourse/discourse/releases/tag/v2026.1.5
- https://github.com/discourse/discourse/releases/tag/v2026.4.2
- https://github.com/discourse/discourse/releases/tag/v2026.5.1
- https://github.com/discourse/discourse/releases/tag/v2026.6.0
- https://github.com/discourse/discourse/security/advisories/GHSA-8f9m-v436-wr3x
- https://nvd.nist.gov/vuln/detail/CVE-2026-53961
