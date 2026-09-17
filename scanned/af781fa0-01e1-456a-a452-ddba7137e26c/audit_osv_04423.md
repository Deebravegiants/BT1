# [M] Discourse secure uploads accessible to guests even when login is required

## Summary
Severity: Medium
Advisory: BIT-discourse-2023-49099
Aliases: CVE-2023-49099, GHSA-j67x-x6mq-pwv4
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-discourse-2023-49099
Type: osv

## Affected
- Bitnami: `discourse` — affected >=0 <3.1.4

## Details
Discourse is a platform for community discussion. Under very specific circumstances, secure upload URLs associated with posts can be accessed by guest users even when login is required. This vulnerability has been patched in 3.2.0.beta4 and 3.1.4.

## References
- https://github.com/discourse/discourse/commit/1b288236387fc0a823e4f15f1aea8dde81b49d53
- https://github.com/discourse/discourse/security/advisories/GHSA-j67x-x6mq-pwv4
- https://nvd.nist.gov/vuln/detail/CVE-2023-49099
