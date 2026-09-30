# [C] Oxia has an OIDC token audience validation bypass via SkipClientIDCheck

## Summary
Severity: Critical
Advisory: GHSA-fhvp-9hcj-6m33
CVE: CVE-2026-40946
CWE: CWE-287
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-04-14
Source: https://github.com/advisories/GHSA-fhvp-9hcj-6m33
Type: github-advisory

## Affected
- Go: `github.com/oxia-db/oxia` — affected >=0 <0.16.2

## Details
### Summary
The OIDC authentication provider unconditionally sets `SkipClientIDCheck: true` in the `go-oidc` verifier configuration, disabling the standard audience (`aud`) claim validation at the library level. This allows tokens issued for unrelated services by the same OIDC issuer to be accepted by Oxia.

### Impact
In deployments using OIDC authentication, an attacker possessing a valid JWT token issued by the same identity provider but intended for a different service (different `client_id`/`aud`) can authenticate to Oxia. This bypasses the intended audience isolation of OAuth2/OIDC.

All versions using OIDC authentication are affected.

### Details
In `oxiad/common/rpc/auth/oidc.go`, both `createStaticKeyVerifier()` and `createRemoteVerifier()` set `SkipClientIDCheck: true`. While a custom audience check exists in `Authenticate()`, the library-level check — which validates the `aud` claim against the expected `client_id` — is completely bypassed.

### Patches
Fixed by removing `SkipClientIDCheck: true` and setting the `ClientID` field from the configured `AllowedAudiences`.

### Workarounds
Ensure network-level isolation so that only trusted services can reach the Oxia gRPC endpoints.

## References
- https://github.com/oxia-db/oxia/security/advisories/GHSA-fhvp-9hcj-6m33
- https://nvd.nist.gov/vuln/detail/CVE-2026-40946
- https://github.com/oxia-db/oxia
