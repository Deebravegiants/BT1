# [M] Fleet vulnerable to SQL Injection in MDM bootstrap package by authenticated team or global admin

## Summary
Severity: Medium
Advisory: GHSA-9p23-p2m4-2r4m
CVE: CVE-2026-34386
CWE: CWE-89
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:U (CVSS_V4)
Published: 2026-03-30
Source: https://github.com/advisories/GHSA-9p23-p2m4-2r4m
Type: github-advisory

## Affected
- Go: `github.com/fleetdm/fleet/v4` — affected >=0 <4.81.0

## Details
### Summary

A SQL Injection vulnerability in Fleet's MDM bootstrap package configuration allows an authenticated user with Team Admin or Global Admin privileges to modify arbitrary team configurations, exfiltrate sensitive data from the Fleet database, and inject arbitrary content into team configs via direct API calls.

### Impact

An authenticated user with Team Admin or Global Admin role can exploit a flaw in how user-supplied input is handled during MDM bootstrap package configuration. Insufficient server-side input validation allows crafted input to manipulate database queries in unintended ways.

Successful exploitation could enable cross-team data corruption, exfiltration of sensitive information such as password hashes and API tokens, and potential privilege escalation. Exploitation requires authentication with team or global admin privileges and MDM to be enabled.

This issue does not affect instances where Apple MDM is disabled.

### Workarounds

If an immediate upgrade is not possible, affected Fleet users should temporarily disable Apple MDM or limit admin roles.

### For more information

If there are any questions or comments about this advisory:

Send an email to  [security@fleetdm.com](mailto:security@fleetdm.com)

Join #fleet in [osquery Slack](https://join.slack.com/t/osquery/shared_invite/zt-h29zm0gk-s2DBtGUTW4CFel0f0IjTEw)

### Credits

Fleet thanks the Secfox Research Team (@secfox-ai) for responsibly reporting this issue.

## References
- https://github.com/fleetdm/fleet/security/advisories/GHSA-9p23-p2m4-2r4m
- https://nvd.nist.gov/vuln/detail/CVE-2026-34386
- https://github.com/fleetdm/fleet
