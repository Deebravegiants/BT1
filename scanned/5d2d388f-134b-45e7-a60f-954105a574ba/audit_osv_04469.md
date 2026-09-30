# [M] Users are able to find users by name even when `enable_names` is off

## Summary
Severity: Medium
Advisory: BIT-discourse-2025-64528
Aliases: CVE-2025-64528, GHSA-c59w-jwx7-34v4
Ecosystem: Bitnami
Published: 2026-01-08
Source: https://osv.dev/vulnerability/BIT-discourse-2025-64528
Type: osv

## Affected
- Bitnami: `discourse` — affected >=2025.11.0 <2025.11.1

## Details
Discourse is an open source discussion platform. Prior to versions 3.5.3, 2025.11.1, and 2025.12.0, an attacker who knows part of a username can find the user and their full name via UI or API, even when `enable_names` is disabled. Versions 3.5.3, 2025.11.1, and 2025.12.0 contain a fix.

## References
- https://github.com/discourse/discourse/commit/1cb45b8b287597085e3514596ffb1d9b41938f81
- https://github.com/discourse/discourse/commit/6192f55629624925595dae14364fd86cac0f09df
- https://github.com/discourse/discourse/commit/e936a523b5900a9d866d23ea3da904ba12bb0fb2
- https://github.com/discourse/discourse/security/advisories/GHSA-c59w-jwx7-34v4
- https://nvd.nist.gov/vuln/detail/CVE-2025-64528
