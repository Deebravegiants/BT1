# [M] Velociraptor vulnerable to privilege escalation via UpdateConfig artifact

## Summary
Severity: Medium
Advisory: GHSA-gpfc-mph4-qm24
CVE: CVE-2025-6264
CWE: CWE-276
Ecosystem: Go
CVSS: CVSS:3.1/AV:L/AC:H/PR:H/UI:R/S:C/C:L/I:L/A:L (CVSS_V3)
Published: 2025-06-20
Source: https://github.com/advisories/GHSA-gpfc-mph4-qm24
Type: github-advisory

## Affected
- Go: `www.velocidex.com/golang/velociraptor` — affected >=0 <0.74.3

## Details
Velociraptor allows collection of VQL queries packaged into Artifacts from endpoints. These artifacts can be used to do anything and usually run with elevated permissions.  To limit access to some dangerous artifact, Velociraptor allows for those to require high permissions like EXECVE to launch.

The Admin.Client.UpdateClientConfig is an artifact used to update the client's configuration. This artifact did not enforce an additional required permission, allowing users with COLLECT_CLIENT permissions (normally given by the "Investigator" role) to collect it from endpoints and update the configuration. 

This can lead to arbitrary command execution and endpoint takeover.

To successfully exploit this vulnerability the user must already have access to collect artifacts from the endpoint (i.e. have the COLLECT_CLIENT given typically by the "Investigator' role).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-6264
- https://github.com/Velocidex/velociraptor/commit/21e7fd7138ddaa798cad35fd929864f6bb0c4e9c
- https://blog.talosintelligence.com/velociraptor-leveraged-in-ransomware-attacks
- https://docs.velociraptor.app/announcements/advisories/cve-2025-6264
- https://github.com/Velocidex/velociraptor
- https://news.sophos.com/en-us/2025/08/26/velociraptor-incident-response-tool-abused-for-remote-access
