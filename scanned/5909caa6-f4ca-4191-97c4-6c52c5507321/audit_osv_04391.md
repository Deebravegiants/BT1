# [H] Discourse vulnerable to SSRF protection bypass possible with IPv4-mapped IPv6 addresses

## Summary
Severity: High
Advisory: BIT-discourse-2023-28111
Aliases: CVE-2023-28111, GHSA-26h3-8ww8-v5fc
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-discourse-2023-28111
Type: osv

## Affected
- Bitnami: `discourse` — affected >=0 <3.1.0

## Details
Discourse is an open-source discussion platform. Prior to version 3.1.0.beta3 of the `beta` and `tests-passed` branches, attackers are able to bypass Discourse's server-side request forgery (SSRF) protection for private IPv4 addresses by using a IPv4-mapped IPv6 address. The issue is patched in the latest beta and tests-passed version of Discourse. version 3.1.0.beta3 of the `beta` and `tests-passed` branches. There are no known workarounds.

## References
- https://github.com/discourse/discourse/commit/fd16eade7fcc6bba4b71e71106a2eb13cdfdae4a
- https://github.com/discourse/discourse/pull/20710
- https://github.com/discourse/discourse/security/advisories/GHSA-26h3-8ww8-v5fc
- https://nvd.nist.gov/vuln/detail/CVE-2023-28111
