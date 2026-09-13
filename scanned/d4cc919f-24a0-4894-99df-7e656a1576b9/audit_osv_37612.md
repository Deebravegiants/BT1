# [H] ZITADEL SCIM Authentication Bypass via URL Encoding

## Summary
Severity: High
Advisory: CVE-2026-32130
Aliases: GHSA-83pv-4xxp-rm2x
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-03-11
Source: https://osv.dev/vulnerability/CVE-2026-32130
Type: osv

## Details
ZITADEL is an open source identity management platform. From 2.68.0 to before 3.4.8 and 4.12.2, Zitadel provides a System for Cross-domain Identity Management (SCIM) API to provision users from external providers into Zitadel. Request to the API with URL-encoded path values were correctly routed but would bypass necessary authentication and permission checks. This allowed unauthenticated attackers to retrieve sensitive information such as names, email addresses, phone numbers, addresses, external IDs, and roles. Note that due to additional checks when manipulating data, an attacker could not modify or delete any user data. This vulnerability is fixed in 3.4.8 and 4.12.2.

## References
- https://github.com/zitadel/zitadel/releases/tag/v3.4.8
- https://github.com/zitadel/zitadel/releases/tag/v4.12.2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/32xxx/CVE-2026-32130.json
- https://github.com/zitadel/zitadel/security/advisories/GHSA-83pv-4xxp-rm2x
- https://nvd.nist.gov/vuln/detail/CVE-2026-32130
