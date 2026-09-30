# [M] ChurchCRM has Missing Object-Level Authorization / IDOR in `/api/person/{personId}`

## Summary
Severity: Medium
Advisory: CVE-2026-40480
Aliases: GHSA-5w59-32c8-933v
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-04-17
Source: https://osv.dev/vulnerability/CVE-2026-40480
Type: osv

## Details
ChurchCRM is an open-source church management system. In versions prior to 7.2.0, the GET /api/person/{personId} endpoint loads and returns person records without performing object-level authorization checks. Although the legacy PersonView.php page enforces canEditPerson() restrictions, the API layer omits this check. Any authenticated user with only EditSelf privileges can enumerate and read other members' records, exposing sensitive PII including names, addresses, phone numbers, and email addresses. This issue has been fixed in version 7.2.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/40xxx/CVE-2026-40480.json
- https://github.com/ChurchCRM/CRM/security/advisories/GHSA-5w59-32c8-933v
- https://nvd.nist.gov/vuln/detail/CVE-2026-40480
- https://github.com/ChurchCRM/CRM/issues/8617
- https://github.com/ChurchCRM/CRM/commit/28ea7a2965fc2fe30e150fadb1ae38a97f8225c2
- https://github.com/ChurchCRM/CRM/pull/8616
