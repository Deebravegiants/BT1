# [M] Velociraptor VFSGetBuffer API path deny list bypass

## Summary
Severity: Medium
Advisory: CVE-2026-18636
CVSS: 6.8 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:H/I:N/A:N)
Published: 2026-08-11
Source: https://osv.dev/vulnerability/CVE-2026-18636
Type: osv

## Details
The Velociraptor gRPC API has a VFSGetBuffer endpoint which allows reading files from the datastore. To prevent users from reading sensitive files or accessing other orgs, the requested path is prefix checked against a list of denied prefixes. This prefix check can be bypassed allowing a user to access usually denied files. If the user has read permission in the ROOT org, this allows access to other orgs, in which the user may not have permission.

## References
- https://github.com/Velocidex/velociraptor/
- http://docs.velociraptor.app/announcements/advisories/cve-2026-18636/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/18xxx/CVE-2026-18636.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-18636
