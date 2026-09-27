# [C] Kimai before 2.64.0 Missing Authorization via ProjectViewController export

## Summary
Severity: Critical
Advisory: CVE-2026-80194
Aliases: GHSA-pvc4-crg3-gj44
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-25
Source: https://osv.dev/vulnerability/CVE-2026-80194
Type: osv

## Details
Kimai before 2.64.0 contains a missing authorization vulnerability in the ProjectViewController export route (report_project_view_export). The authorization guards are attached to the sibling __invoke method rather than at the class level, so the export route inherits no authorization checks. Any authenticated user, including a plain ROLE_USER without the project_reporting permission, can download the project overview export - which returns the same dataset as the protected report - disclosing customer names, project names, currency, budget type, and aggregate totals across all customers. Actual financial figures remain protected in the export template.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/80xxx/CVE-2026-80194.json
- https://github.com/kimai/kimai/security/advisories/GHSA-pvc4-crg3-gj44
- https://nvd.nist.gov/vuln/detail/CVE-2026-80194
- https://www.vulncheck.com/advisories/kimai-before-2.64.0-missing-authorization-via-projectviewcontroller-export
