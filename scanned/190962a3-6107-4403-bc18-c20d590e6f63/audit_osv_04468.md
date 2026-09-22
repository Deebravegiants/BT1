# [M] Discourse is missing Cache-Control response header on error responses

## Summary
Severity: Medium
Advisory: BIT-discourse-2025-61598
Aliases: CVE-2025-61598, GHSA-jp9x-wwv6-cv3j
Ecosystem: Bitnami
Published: 2025-11-06
Source: https://osv.dev/vulnerability/BIT-discourse-2025-61598
Type: osv

## Affected
- Bitnami: `discourse` — affected >=0 <3.6.2

## Details
Discourse is an open source discussion platform. Version before 3.6.2 and 3.6.0.beta2, default Cache-Control response header with value no-store, no-cache was missing from error responses. This may caused unintended caching of those responses by proxies potentially leading to cache poisoning attacks. This vulnerability is fixed in 3.6.2 and 3.6.0.beta2.

## References
- https://github.com/discourse/discourse/commit/3ea1b663c82c067e5ca778db846bad1e082ba6cd
- https://github.com/discourse/discourse/commit/fd567af7bf5a15c70772021acbdf5d38487a31bc
- https://github.com/discourse/discourse/security/advisories/GHSA-jp9x-wwv6-cv3j
- https://nvd.nist.gov/vuln/detail/CVE-2025-61598
