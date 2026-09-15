# [H] Fleet has an Access Control vulnerability in debug/pprof endpoints

## Summary
Severity: High
Advisory: GHSA-4r5r-ccr6-q6f6
CVE: CVE-2026-23517
CWE: CWE-862, CWE-863
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:L/VI:N/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-01-20
Source: https://github.com/advisories/GHSA-4r5r-ccr6-q6f6
Type: github-advisory

## Affected
- Go: `github.com/fleetdm/fleet` — affected >=4.78.0 <4.78.3
- Go: `github.com/fleetdm/fleet` — affected >=4.77.0 <4.77.1
- Go: `github.com/fleetdm/fleet` — affected >=4.76.0 <4.76.2
- Go: `github.com/fleetdm/fleet` — affected >=4.75.0 <4.75.2
- Go: `github.com/fleetdm/fleet/v4` — affected >=0 <4.78.3-0.20260112221730-5c030e32a3a9

## Details
### Summary

A broken access control issue in Fleet allowed authenticated users to access debug and profiling endpoints regardless of role. As a result, low-privilege users could view internal server diagnostics and trigger resource-intensive profiling operations.

### Impact

Fleet’s debug/pprof endpoints are accessible to any authenticated user regardless of role, including the lowest-privilege “Observer” role. This allows low-privilege users to access sensitive server internals, including runtime profiling data and in-memory application state, and to trigger CPU-intensive profiling operations that could lead to denial of service.

### Patches

- 4.78.3
- 4.77.1
- 4.76.2
- 4.75.2
- 4.53.3

### Workarounds

If an immediate upgrade is not possible, users should put the debug/pprof endpoints behind an IP allowlist. 

### For more information

If you have any questions or comments about this advisory:

Email us at [security@fleetdm.com](mailto:security@fleetdm.com)
Join #fleet in [osquery Slack](https://join.slack.com/t/osquery/shared_invite/zt-h29zm0gk-s2DBtGUTW4CFel0f0IjTEw)

### Credits

We thank @secfox-ai for responsibly reporting this issue.

## References
- https://github.com/fleetdm/fleet/security/advisories/GHSA-4r5r-ccr6-q6f6
- https://nvd.nist.gov/vuln/detail/CVE-2026-23517
- https://github.com/fleetdm/fleet/commit/5c030e32a3a9bc512355b5e1bf19636e4e6d0317
- https://github.com/fleetdm/fleet
- https://pkg.go.dev/vuln/GO-2026-4334
