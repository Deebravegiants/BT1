# [M] RansomLook Unauthenticated Database Export Exposes Private Data

## Summary
Severity: Medium
Advisory: CVE-2026-78370
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:H/SI:N/SA:N)
Published: 2026-08-24
Source: https://osv.dev/vulnerability/CVE-2026-78370
Type: osv

## Details
RansomLook contains an authorization flaw in its legacy database export functionality that can allow unauthenticated remote users to retrieve information intended to remain private.

The /export/<database> endpoint permits selected internal databases to be exported without requiring authentication. While limited filtering is performed for some entity databases, other exportable databases are returned directly without consistently applying the application's private-entity access restrictions. As a result, information associated with groups, markets, posts, or other records marked as private may be included in an export accessible to an unauthenticated requester.

An attacker able to reach the RansomLook web application can request the affected export endpoint and retrieve data that should only be available to authorized users. Depending on the contents of the instance, this may disclose private ransomware intelligence, victim information, internal tracking data, or other information deliberately excluded from public views.

The patch removes the legacy unauthenticated export route and introduces centralized authorization handling that distinguishes ordinary authenticated API access from authorization to view private entries. API keys must now be explicitly granted private-data access, while existing keys do not automatically receive this privilege. The same private-data filtering is also applied consistently across API responses and database exports.

## References
- https://github.com/RansomLook/RansomLook/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/78xxx/CVE-2026-78370.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-78370
- https://github.com/RansomLook/RansomLook/commit/ff97a3489d70ffc3c1d09ea2c7d25137edfffb2a
