# [M] EspoCRM: IDOR in EmailTemplate Prepare Endpoint Leaks Entity Data via Email Address Lookup

## Summary
Severity: Medium
Advisory: CVE-2026-41141
Aliases: GHSA-vvmh-mf4h-96hw
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-05-28
Source: https://osv.dev/vulnerability/CVE-2026-41141
Type: osv

## Details
EspoCRM is an open source customer relationship management application. Prior to 9.3.5, the POST /api/v1/EmailTemplate/:id/prepare endpoint accepts an emailAddress parameter and resolves the owning entity (Contact, Lead, Account, or User) without performing an ACL check. An authenticated user with EmailTemplate read permission can extract all field values of any entity by supplying the target's email address, bypassing read: own or read: team ACL restrictions. This vulnerability is fixed in 9.3.5.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/41xxx/CVE-2026-41141.json
- https://github.com/espocrm/espocrm/security/advisories/GHSA-vvmh-mf4h-96hw
- https://nvd.nist.gov/vuln/detail/CVE-2026-41141
