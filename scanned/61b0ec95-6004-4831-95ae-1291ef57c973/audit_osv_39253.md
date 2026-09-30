# [M] OpenProject: Business Logic Error on OpenProject through PATCH request to /api/v3/users/me permits to bypass password requirements

## Summary
Severity: Medium
Advisory: CVE-2026-44733
Aliases: GHSA-px7f-cj9f-7m4m
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:L/A:N)
Published: 2026-06-26
Source: https://osv.dev/vulnerability/CVE-2026-44733
Type: osv

## Details
OpenProject is open-source, web-based project management software. Prior to 17.3.2 and 17.4.0, Business Logic Error on OpenProject through PATCH request to /api/v3/users/me permits to bypass password requirements. A password validation flaw in the change password behavior allows attackers to change a user's password only with an active session takeover. This vulnerability is fixed in 17.3.2 and 17.4.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/44xxx/CVE-2026-44733.json
- https://github.com/opf/openproject/security/advisories/GHSA-px7f-cj9f-7m4m
- https://nvd.nist.gov/vuln/detail/CVE-2026-44733
