# [H] Oxia exposes bearer token in debug log messages on authentication failure

## Summary
Severity: High
Advisory: GHSA-pm7q-rjjx-979p
CVE: CVE-2026-40945
CWE: CWE-532
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N/E:X/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X (CVSS_V4)
Published: 2026-04-14
Source: https://github.com/advisories/GHSA-pm7q-rjjx-979p
Type: github-advisory

## Affected
- Go: `github.com/oxia-db/oxia` — affected >=0 <0.16.2

## Details
### Summary
When OIDC authentication fails, the full bearer token is logged at DEBUG level in plaintext. If debug logging is enabled in production, JWT tokens are exposed in application logs and any connected log aggregation system.

### Impact
An attacker with access to application logs (e.g., via a compromised log aggregation pipeline, shared logging infrastructure, or misconfigured log access controls) can extract valid JWT tokens and replay them to authenticate as legitimate users.

All versions using OIDC authentication are affected.

### Details
In `oxiad/common/rpc/auth/interceptor.go`, the `validateTokenWithContext()` function logs the complete token value via `slog.String("token", token)` when authentication fails. This includes the full JWT header, payload, and signature.

### Patches
Fixed by redacting the token in log output — only the last 8 characters are preserved for correlation purposes.

### Workarounds
Ensure DEBUG-level logging is never enabled in production environments.

## References
- https://github.com/oxia-db/oxia/security/advisories/GHSA-pm7q-rjjx-979p
- https://nvd.nist.gov/vuln/detail/CVE-2026-40945
- https://github.com/oxia-db/oxia/commit/f7259d0ebc739fc95ff19f93c823433850857416
- https://github.com/oxia-db/oxia
