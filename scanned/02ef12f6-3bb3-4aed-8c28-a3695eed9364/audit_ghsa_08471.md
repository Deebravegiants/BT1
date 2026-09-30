# [H] Free5GC PCF: Missing authentication middleware in Npcf_SMPolicyControl allows access to SM policy handlers and disclosure of subscriber SUPI

## Summary
Severity: High
Advisory: GHSA-6rgm-gr97-x3j5
CVE: CVE-2026-42083
CWE: CWE-862
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2026-05-07
Source: https://github.com/advisories/GHSA-6rgm-gr97-x3j5
Type: github-advisory

## Affected
- Go: `github.com/free5gc/pcf` — affected >=0 <1.4.3

## Details
### Summary
PCF Npcf_SMPolicyControl missing authentication middleware allows unauthenticated access to SM policy handlers and disclosure of subscriber SUPI
### Details
In `NewServer()`, the `smPolicyGroup` route group is created and routes are applied without attaching the router authorization middleware. In contrast, other PCF service groups such as `Npcf_PolicyAuthorization` do attach `RouterAuthorizationCheck` before route registration.

Because the middleware is missing, requests to the following endpoints can reach business logic even when no valid OAuth token is provided:

- `POST /npcf-smpolicycontrol/v1/sm-policies`
- `GET /npcf-smpolicycontrol/v1/sm-policies/{smPolicyId}`
- `POST /npcf-smpolicycontrol/v1/sm-policies/{smPolicyId}/update`
- `POST /npcf-smpolicycontrol/v1/sm-policies/{smPolicyId}/delete`

This is visible at runtime because unauthenticated requests return business-level responses such as `400` or `404` instead of being rejected with `401` before handler execution. Under valid lab preconditions (existing UE/session context and related policy data), unauthenticated `POST /sm-policies` can succeed with `201`, and unauthenticated `GET /sm-policies/{id}` can succeed with `200` and return policy context containing subscriber identifiers including `supi`.

The root cause is missing router auth enforcement for `Npcf_SMPolicyControl`. 
Upstream also fixed this by adding `RouterAuthorizationCheck` to `smPolicyGroup` (and `uePolicyGroup`) in free5gc/pcf PR #63.

### PoC
1. Deploy free5GC with PCF reachable on the SBI network.
2. Use the PoC against the PCF service **without** an `Authorization` header:
   ```bash
   go run /home/ubuntu/free5gc/tools/npcf-smpolicy-noauth-poc/main.go \
     --pcf-root /home/ubuntu/free5gc/NFs/pcf \
     --pcf-url http://10.100.200.9:8000 \
     --timeout 4s
Observe that unauthenticated requests to Npcf_SMPolicyControl return business responses instead of 401.
### Impact

This is an authentication/authorization bypass on a network-accessible SBI service. Any unauthenticated actor able to reach the PCF SBI interface can invoke Npcf_SMPolicyControl handlers directly.

## References
- https://github.com/free5gc/free5gc/security/advisories/GHSA-6rgm-gr97-x3j5
- https://nvd.nist.gov/vuln/detail/CVE-2026-42083
- https://github.com/free5gc/free5gc/issues/844
- https://github.com/free5gc/pcf/pull/63
- https://github.com/free5gc/pcf/commit/8c4d457cdf58bb239ee30e88c56b370b22073964
- https://github.com/free5gc/free5gc
