# [H] Fleet server may terminate unexpectedly when handling certain gRPC requests

## Summary
Severity: High
Advisory: GHSA-x67p-9m2r-fxqv
CVE: CVE-2026-26062
CWE: CWE-20
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-05-14
Source: https://github.com/advisories/GHSA-x67p-9m2r-fxqv
Type: github-advisory

## Affected
- Go: `github.com/fleetdm/fleet/v4` — affected >=0 <4.81.0

## Details
### Summary

Fleet contained a denial-of-service (DoS) issue in the gRPC Launcher `PublishLogs` endpoint. In affected versions, certain unexpected input values were not handled gracefully, which could cause the Fleet server process to terminate while processing an authenticated request from an enrolled Launcher host.

### Impact

An authenticated attacker with access to any enrolled Launcher node key could cause an immediate and complete denial of service by sending a single gRPC request to the `PublishLogs` endpoint.

This vulnerability impacts **availability only**. There is:

- No exposure of sensitive data
- No authentication bypass
- No privilege escalation
- No integrity impact

### Workarounds

If upgrading immediately is not possible, the following mitigations can reduce exposure:

- Restrict network access to the Fleet gRPC endpoint where feasible (for example, limiting inbound access to known host IP ranges).
- Deploy Fleet behind infrastructure that terminates or filters gRPC traffic if Launcher log ingestion is not required.
- Monitor for repeated Fleet process crashes or unexpected restarts indicating potential exploitation.

### For More Information

If you have any questions or concerns about this advisory, please contact us at:

Email us at [security@fleetdm.com](mailto:security@fleetdm.com)

### Credits

We thank @fuzzztf for responsibly reporting this issue.

## References
- https://github.com/fleetdm/fleet/security/advisories/GHSA-x67p-9m2r-fxqv
- https://nvd.nist.gov/vuln/detail/CVE-2026-26062
- https://github.com/fleetdm/fleet
- https://github.com/fleetdm/fleet/releases/tag/fleet-v4.81.0
