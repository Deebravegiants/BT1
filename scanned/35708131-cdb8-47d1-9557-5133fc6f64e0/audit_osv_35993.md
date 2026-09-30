# [H] Velociraptor query plugin allows impersonation in other orgs

## Summary
Severity: High
Advisory: CVE-2026-18635
CVSS: 7.2 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-11
Source: https://osv.dev/vulnerability/CVE-2026-18635
Type: osv

## Details
Velociraptor's VQL has a query() plugin which allows running a VQL query in a different org or user context. To be able to run as a different user, the calling user needs to have the IMPERSONATE permission (usually only given to administrators). Velociraptor versions prior to 0.77.2 evaluate this permission against the caller's org instead of against the target org.

This allows an administrator in one org to impersonate another user in another org, in which they may not have the IMPERSONATE permission.

## References
- https://github.com/Velocidex/velociraptor/
- http://docs.velociraptor.app/announcements/advisories/cve-2026-18635/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/18xxx/CVE-2026-18635.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-18635
