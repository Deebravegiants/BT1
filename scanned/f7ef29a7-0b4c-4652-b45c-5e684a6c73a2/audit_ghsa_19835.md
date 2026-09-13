# [M] buildx allows a possible credential leakage to telemetry endpoint

## Summary
Severity: Medium
Advisory: GHSA-m4gq-fm9h-8q75
CVE: CVE-2025-0495
CWE: CWE-532
Ecosystem: Go
CVSS: CVSS:4.0/AV:L/AC:L/AT:N/PR:L/UI:P/VC:L/VI:N/VA:N/SC:H/SI:N/SA:N (CVSS_V4)
Published: 2025-03-17
Source: https://github.com/advisories/GHSA-m4gq-fm9h-8q75
Type: github-advisory

## Affected
- Go: `github.com/docker/buildx` — affected >=0 <0.21.3

## Details
### Impact
Some cache backends allow configuring their credentials by setting secrets directly as attribute values in `cache-to/cache-from` configuration. If this was done by the user, these secure values could be captured together with OpenTelemetry trace as part of the arguments and flags for the traced CLI command. Passing tokens to Github cache backend via environment variables or using registry authentication is not affected.

If you passed a token value like this and use a custom OpenTelemetry collector for computing traces you should make sure that your traces are kept secure. OpenTelemetry traces are also saved in BuildKit daemon's history records.

### Patches
Issue has been fixed in Buildx v0.21.3 or newer.

### Workarounds
Avoid passing cache backend credentials with CLI arguments. Make sure access to traces and BuildKit history records is kept secure.

## References
- https://github.com/docker/buildx/security/advisories/GHSA-m4gq-fm9h-8q75
- https://nvd.nist.gov/vuln/detail/CVE-2025-0495
- https://github.com/docker/buildx/commit/18ccba072076ddbfb0aeedd6746d7719b0729b58
- https://github.com/docker/buildx
