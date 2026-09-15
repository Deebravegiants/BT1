# [M] Istio: AuthorizationPolicy serviceAccounts regex injection via unescaped dots

## Summary
Severity: Medium
Advisory: GHSA-9gcg-w975-3rjh
CVE: CVE-2026-39350
CWE: CWE-185
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2026-04-16
Source: https://github.com/advisories/GHSA-9gcg-w975-3rjh
Type: github-advisory

## Affected
- Go: `istio.io/istio` — affected >=0.0.0-20241024090207-0bf27d49ba4b <0.0.0-20260403004500-692e460c342d

## Details
### Impact
The `serviceAccounts` and `notServiceAccounts` fields in AuthorizationPolicy incorrectly interpret dots (`.`) as a regular expression matcher. Because `.` is a valid character in a service account name, an `AuthorizationPolicy` ALLOW rule targeting SA e.g. `cert-manager.io` also matches `cert-manager-io`, `cert-managerXio`, etc. A DENY rule targeting the same name fails to block those variants.

### Patches
Fixes are available in 1.29.2, 1.28.6, and 1.27.9

### Workarounds
None

## References
- https://github.com/istio/istio/security/advisories/GHSA-9gcg-w975-3rjh
- https://nvd.nist.gov/vuln/detail/CVE-2026-39350
- https://github.com/istio/istio/commit/692e460c342d8f308a35b6ecbdace47807da8ade
- https://github.com/istio/istio
