# [M] Nextcloud Server Contacts Search allowed users to retrieve contact information of other users beyond their contact list

## Summary
Severity: Medium
Advisory: BIT-nextcloud-2025-66510
Aliases: CVE-2025-66510, GHSA-495w-cqv6-wr59
Ecosystem: Bitnami
Published: 2026-07-13
Source: https://osv.dev/vulnerability/BIT-nextcloud-2025-66510
Type: osv

## Affected
- Bitnami: `nextcloud` — affected >=32.0.0 <32.0.1

## Details
Nextcloud Server is a self hosted personal cloud system. In Nextcloud Server prior to 31.0.10 and 32.0.1 and Nextcloud Enterprise Server prior to 28.0.14.11, 29.0.16.8, 30.0.17.3, and 31.0.10, contacts search allowed to retrieve personal data of other users (emails, names, identifiers) without proper access control. This allows an authenticated user to retrieve information about accounts that are not related or added as contacts.

## References
- https://github.com/nextcloud/security-advisories/security/advisories/GHSA-495w-cqv6-wr59
- https://github.com/nextcloud/server/commit/e4866860cbf24a746eb8a125587262a4c8831c57
- https://github.com/nextcloud/server/pull/55657
- https://nvd.nist.gov/vuln/detail/CVE-2025-66510
