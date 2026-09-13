# [M] Velociraptor Hunt Deletion With Insufficient Permission Check

## Summary
Severity: Medium
Advisory: CVE-2026-64952
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N)
Published: 2026-08-12
Source: https://osv.dev/vulnerability/CVE-2026-64952
Type: osv

## Details
The hunt_delete() VQL function allows deleting hunts. 

Velociraptor misapplied the permission check requiring only COLLECT_CLIENT (usually assigned to the "investigator" role) instead of the "DELETE_RESULTS" permission (usually only assigned to "administrators").

## References
- https://github.com/Velocidex/velociraptor/
- http://docs.velociraptor.app/announcements/advisories/cve-2026-64952/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64952.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64952
