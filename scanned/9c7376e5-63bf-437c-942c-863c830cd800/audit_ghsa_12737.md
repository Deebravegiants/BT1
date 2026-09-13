# [M] Velociraptor subject to Path Traversal

## Summary
Severity: Medium
Advisory: GHSA-7jf5-fvgf-48c6
CVE: CVE-2023-0290
CWE: CWE-22
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2023-01-19
Source: https://github.com/advisories/GHSA-7jf5-fvgf-48c6
Type: github-advisory

## Affected
- Go: `www.velocidex.com/golang/velociraptor` — affected >=0 <0.6.7-5

## Details
Rapid7 Velociraptor did not properly sanitize the client ID parameter to the CreateCollection API, allowing a directory traversal in where the collection task could be written. It was possible to provide a client id of "../clients/server" to schedule the collection for the server (as a server artifact), but only require privileges to schedule collections on the client. Normally, to schedule an artifact on the server, the COLLECT_SERVER permission is required. This permission is normally only granted to "administrator" role. Due to this issue, it is sufficient to have the COLLECT_CLIENT privilege, which is normally granted to the "investigator" role. To exploit this vulnerability, the attacker must already have a Velociraptor user account at least "investigator" level, and be able to authenticate to the GUI and issue an API call to the backend. Typically, most users deploy Velociraptor with limited access to a trusted group, and most users will already be administrators within the GUI. This issue affects Velociraptor versions before 0.6.7-5. Version 0.6.7-5, released January 16, 2023, fixes the issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-0290
- https://github.com/Velocidex/velociraptor/commit/4718bb0cb426564568abc77910e90a2c211a32e6
- https://github.com/Velocidex/velociraptor
- https://github.com/Velocidex/velociraptor/compare/v0.6.7-4...v0.6.7-5
