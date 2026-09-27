# [M] Velociraptor STACK Type Download Path Bypasses Denied Prefix Check

## Summary
Severity: Medium
Advisory: CVE-2026-18652
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-08-12
Source: https://osv.dev/vulnerability/CVE-2026-18652
Type: osv

## Details
Velociraptor allows reading Stacked result sets from the GUI.  Velociraptor's multi-tenant design stores sub orgs within the datastore directory. The path requested by the GUI is not correctly checked against the prefix deny list, allowing result sets to read from denied prefixes.

In particular, a user with read access to the root org can access result sets from child orgs.

## References
- https://github.com/Velocidex/velociraptor/
- http://docs.velociraptor.app/announcements/advisories/cve-2026-18652/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/18xxx/CVE-2026-18652.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-18652
