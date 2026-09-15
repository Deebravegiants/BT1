# [H] Velociraptor collect_client() Permissions Bypass

## Summary
Severity: High
Advisory: CVE-2026-64954
CVSS: 8.2 (CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:C/C:H/I:H/A:N)
Published: 2026-08-12
Source: https://osv.dev/vulnerability/CVE-2026-64954
Type: osv

## Details
Velociraptor allows scheduling new collections via VQL queries in notebooks. For a user to schedule a new collection, they require the COLLECT_CLIENT permission. However, this is not enforced when the user can run a VQL query which resets the authorization provider.

This allows a user who can run arbitrary VQL (usually with the "analyst" role) to launch new collections (usually requires the "investigator" role). This vulnerability is an escalation from an analyst to investigator role.

## References
- https://github.com/Velocidex/velociraptor/
- http://docs.velociraptor.app/announcements/advisories/cve-2026-64954/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64954.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64954
- https://github.com/Velocidex/velociraptor/commit/d7de958e846d3742a7a3a8538fd463e4f12fc528
