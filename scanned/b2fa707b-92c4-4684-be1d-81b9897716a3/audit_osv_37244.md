# [M] OpenProject users that are not project members can be used to calculate Labor Budget, leaking their global hourly rate

## Summary
Severity: Medium
Advisory: CVE-2026-30236
Aliases: GHSA-p747-569x-3v3f
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2026-03-11
Source: https://osv.dev/vulnerability/CVE-2026-30236
Type: osv

## Details
OpenProject is an open-source, web-based project management software. Prior to 17.2.0, when editing a project budget and planning the labor cost, it was not checked that the user that was planned in the budget is actually a project member. This exposed the user's default rate (if one was set up) to users that should only see that information for project members. Also, the endpoint that handles the pre-calculation for the frontend to display a preview of the costs, while it was being entered, did not properly validate the membership of the user as well. This also allowed to calculate costs with the default rate of non-members. This vulnerability is fixed in 17.2.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/30xxx/CVE-2026-30236.json
- https://github.com/opf/openproject/security/advisories/GHSA-p747-569x-3v3f
- https://nvd.nist.gov/vuln/detail/CVE-2026-30236
