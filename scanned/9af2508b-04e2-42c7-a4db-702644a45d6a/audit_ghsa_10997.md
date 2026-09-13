# [M] Fleet vulnerable to Denial of Service via unhandled gRPC log type in launcher endpoint

## Summary
Severity: Medium
Advisory: GHSA-w254-4hp5-7cvv
CVE: CVE-2026-34388
CWE: CWE-703
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N/E:U (CVSS_V4)
Published: 2026-03-30
Source: https://github.com/advisories/GHSA-w254-4hp5-7cvv
Type: github-advisory

## Affected
- Go: `github.com/fleetdm/fleet/v4` — affected >=0 <4.81.0

## Details
### Summary

A Denial of Service vulnerability in Fleet's gRPC Launcher endpoint allows an authenticated host to crash the entire Fleet server process by sending an unexpected log type value. The server terminates immediately, disrupting all connected hosts, MDM enrollments, and API consumers.

### Impact

An attacker with access to a valid Launcher node key can send a specially crafted gRPC request to the Fleet server that triggers an unrecoverable server crash. The gRPC server lacks appropriate error recovery handling, meaning the entire Fleet process terminates rather than gracefully rejecting the malformed input.

Because the crash is instant and repeatable, an attacker could script repeated requests to prevent the server from recovering, resulting in a persistent denial of service until a patched version is deployed.

### Workarounds

There is no workaround for this issue other than upgrading to a patched version.

### For more information

If there are any questions or comments about this advisory:

Send an email to  [security@fleetdm.com](mailto:security@fleetdm.com)

Join #fleet in [osquery Slack](https://join.slack.com/t/osquery/shared_invite/zt-h29zm0gk-s2DBtGUTW4CFel0f0IjTEw)

### Credits

Fleet thanks @fuzzztf for responsibly reporting this issue.

## References
- https://github.com/fleetdm/fleet/security/advisories/GHSA-w254-4hp5-7cvv
- https://nvd.nist.gov/vuln/detail/CVE-2026-34388
- https://github.com/fleetdm/fleet
