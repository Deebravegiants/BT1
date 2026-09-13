# [M] e107: Broken Access Control in e107 comment edit allows cross-user comment modification

## Summary
Severity: Medium
Advisory: CVE-2026-43934
Aliases: GHSA-5w63-63rh-99q6
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N)
Published: 2026-05-26
Source: https://osv.dev/vulnerability/CVE-2026-43934
Type: osv

## Details
e107 is a content management system (CMS). Prior to 2.3.4, a Broken Access Control vulnerability exists in the application, allowing an unauthorized authenticated user to edit comments posted by others. This stems from inadequate server-side access control validation, where the application depends only on a predictable identifier in the request to determine which comment to edit, without confirming the requesting user’s ownership of the comment. This vulnerability is fixed in 2.3.4.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/43xxx/CVE-2026-43934.json
- https://github.com/e107inc/e107/security/advisories/GHSA-5w63-63rh-99q6
- https://nvd.nist.gov/vuln/detail/CVE-2026-43934
- https://github.com/e107inc/e107/commit/23961a8f
