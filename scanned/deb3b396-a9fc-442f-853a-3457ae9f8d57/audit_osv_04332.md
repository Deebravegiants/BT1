# [M] BIT-discourse-2020-24327

## Summary
Severity: Medium
Advisory: BIT-discourse-2020-24327
Aliases: CVE-2020-24327
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-discourse-2020-24327
Type: osv

## Affected
- Bitnami: `discourse` — affected >=2.6.0 <2.6.1

## Details
Server Side Request Forgery (SSRF) vulnerability exists in Discourse 2.3.2 and 2.6 via the email function. When writing an email in an editor, you can upload pictures of remote websites.

## References
- https://github.com/discourse/discourse/pull/10509
- https://github.com/purple-WL/Discourse-sending-email-function-exist-Server-side-request-forgery-SSRF-/issues/1
- https://nvd.nist.gov/vuln/detail/CVE-2020-24327
