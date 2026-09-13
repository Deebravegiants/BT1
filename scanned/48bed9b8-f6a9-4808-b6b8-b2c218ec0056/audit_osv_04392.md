# [H] Discourse's SSRF protection missing for some FastImage requests

## Summary
Severity: High
Advisory: BIT-discourse-2023-28112
Aliases: CVE-2023-28112, GHSA-9897-x229-55gh
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-discourse-2023-28112
Type: osv

## Affected
- Bitnami: `discourse` — affected >=0 <3.1.0

## Details
Discourse is an open-source discussion platform. Prior to version 3.1.0, some user provided URLs were being passed to FastImage without SSRF protection. Insufficient protections could enable attackers to trigger outbound network connections from the Discourse server to private IP addresses. This affects any site running the version 3.1.0 and prior. This issue is patched in version 3.1.0. There are no known workarounds.

## References
- https://github.com/discourse/discourse/commit/39c2f63b35d90ebaf67b9604cf1d424e5984203c
- https://github.com/discourse/discourse/pull/20710
- https://github.com/discourse/discourse/security/advisories/GHSA-9897-x229-55gh
- https://nvd.nist.gov/vuln/detail/CVE-2023-28112
