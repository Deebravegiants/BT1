# [M] Fleet's Apple MDM profile delivery has second-order SQL Injection that can compromise the database

## Summary
Severity: Medium
Advisory: GHSA-v895-833r-8c45
CVE: CVE-2026-34385
CWE: CWE-89
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N/E:U (CVSS_V4)
Published: 2026-03-30
Source: https://github.com/advisories/GHSA-v895-833r-8c45
Type: github-advisory

## Affected
- Go: `github.com/fleetdm/fleet/v4` — affected >=0 <4.81.0

## Details
### Summary

A critical second-order SQL Injection vulnerability in Fleet's Apple MDM profile delivery pipeline could allow an attacker with a valid MDM enrollment certificate to exfiltrate or modify the contents of the Fleet database, including user credentials, API tokens, and device enrollment secrets.

### Impact

If Apple MDM is enabled, an attacker controlling an enrolled device can send a malicious UDID during the MDM Authenticate check-in. The UDID is stored safely via parameterized queries, but is later interpolated directly into SQL when the async worker processes the job. This enables blind, boolean-based, and UNION-based SQL injection across four simultaneous subqueries.

Because Fleet's database driver is configured with `multiStatements=true`, the attacker can also execute stacked queries, enabling arbitrary writes to the database. This includes inserting new admin accounts, modifying configuration, deploying malicious profiles or scripts to managed devices, and deleting data.

Exploitation requires a valid SCEP-issued enrollment certificate (mTLS), but any enrolled device, including attacker-controlled devices, can exploit this vulnerability.

This issue does not affect instances where Apple MDM is disabled.

### Workarounds

If an immediate upgrade is not possible, affected Fleet users should temporarily disable Apple MDM.

### For more information

If there are any questions or comments about this advisory:

Send an email to [security@fleetdm.com](mailto:security@fleetdm.com)

Join #fleet in [[osquery Slack](https://join.slack.com/t/osquery/shared_invite/zt-h29zm0gk-s2DBtGUTW4CFel0f0IjTEw)](https://join.slack.com/t/osquery/shared_invite/zt-h29zm0gk-s2DBtGUTW4CFel0f0IjTEw)

### Credits

Fleet thanks@secfox-ai for responsibly reporting this issue.

## References
- https://github.com/fleetdm/fleet/security/advisories/GHSA-v895-833r-8c45
- https://nvd.nist.gov/vuln/detail/CVE-2026-34385
- https://github.com/fleetdm/fleet
