# [M] Privilege Escalation via Mass Assignment Allows Regular Users to Set Topics as Global Banners

## Summary
Severity: Medium
Advisory: BIT-discourse-2026-28219
Aliases: CVE-2026-28219, GHSA-8v26-9f7h-jc8x
Ecosystem: Bitnami
Published: 2026-03-03
Source: https://osv.dev/vulnerability/BIT-discourse-2026-28219
Type: osv

## Affected
- Bitnami: `discourse` — affected >=2026.1.0 <2026.1.1

## Details
Discourse is an open source discussion platform. Prior to versions 2025.12.2, 2026.1.1, and 2026.2.0, an improper authorization check in the topic management logic allows authenticated users to modify privileged attributes of their topics. By manipulating specific parameters in a PUT or POST request, a regular user can elevate a topic’s status to a site-wide notice or banner, bypassing intended administrative restrictions. Versions 2025.12.2, 2026.1.1, and 2026.2.0 patch the issue. There are no practical workarounds to prevent this behavior other than applying the security patch. Administrators concerned about unauthorized promotions should audit recent changes to site banners and global notices until the fix is deployed.

## References
- https://github.com/discourse/discourse/security/advisories/GHSA-8v26-9f7h-jc8x
- https://nvd.nist.gov/vuln/detail/CVE-2026-28219
