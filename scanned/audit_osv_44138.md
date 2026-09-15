# [C] Kimai before 2.63.0 Team Membership Removal via API

## Summary
Severity: Critical
Advisory: CVE-2026-80195
Aliases: GHSA-6rxf-4hh9-pp46
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-25
Source: https://osv.dev/vulnerability/CVE-2026-80195
Type: osv

## Details
Kimai before 2.63.0 contains a business logic / improper authorization vulnerability in the team update API endpoint (PATCH /api/teams/{id}), which removes all existing team members before validating the submitted replacement member list. An authenticated teamlead (or other user) with permission to edit a team can submit a malformed members payload; although Kimai returns a validation error, the existing membership rows have already been deleted. This bypasses the dedicated member-removal endpoint's protection against removing teamleaders and can leave a team with no members or teamleaders, disrupting team-based access control.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/80xxx/CVE-2026-80195.json
- https://github.com/kimai/kimai/security/advisories/GHSA-6rxf-4hh9-pp46
- https://nvd.nist.gov/vuln/detail/CVE-2026-80195
- https://www.vulncheck.com/advisories/kimai-before-2.63.0-team-membership-removal-via-api
