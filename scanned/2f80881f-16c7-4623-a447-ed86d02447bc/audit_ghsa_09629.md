# [M] Data Sharing Framework is Missing Session Timeout for OIDC Sessions

## Summary
Severity: Medium
Advisory: GHSA-gj7p-595x-qwf5
CVE: CVE-2026-40939
CWE: CWE-613
Ecosystem: Maven
CVSS: CVSS:4.0/AV:P/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-04-15
Source: https://github.com/advisories/GHSA-gj7p-595x-qwf5
Type: github-advisory

## Affected
- Maven: `dev.dsf:dsf-common-jetty` — affected >=0
- Maven: `dev.dsf:dsf-fhir-server` — affected >=0
- Maven: `dev.dsf:dsf-bpe-server` — affected >=0

## Details
### Affected Components
DSF FHIR Server with enabled [OIDC authentication](https://dsf.dev/operations/v2.1.0/fhir/oidc.html).
DSF BPE Server with enabled [OIDC authentication](https://dsf.dev/operations/v2.1.0/bpe/oidc.html).

### Summary
OIDC-authenticated sessions had no configured maximum inactivity timeout. Sessions persisted indefinitely after login, even after the OIDC access token expired.

### Impact
If a user logs in via OIDC and leaves their browser without explicitly logging out, the session remains valid indefinitely. Another person using the same browser can access the DSF UI with the previous user's permissions. This is a realistic threat in hospital environments with shared workstations.

Only affects OIDC browser sessions, not relevant for mTLS machine-to-machine communication.

### Fix (commits f4ecb00, 7d25fea)
- Added configurable session timeout via `dev.dsf.server.auth.oidc.session.timeout` (default: `PT30M`).
- Enabled `logoutWhenIdTokenIsExpired(true)` in OpenID configuration to tie session lifetime to token lifetime.
- Websocket sessions are now closed with `VIOLATED_POLICY` when credentials expire, prevents stale websocket connections from continuing to receive events after session timeout.

## References
- https://github.com/datasharingframework/dsf/security/advisories/GHSA-gj7p-595x-qwf5
- https://nvd.nist.gov/vuln/detail/CVE-2026-40939
- https://github.com/datasharingframework/dsf/commit/7d25feafb83d66cb59985ac88568b67d937b1937
- https://github.com/datasharingframework/dsf/commit/f4ecb002f7d12642f92da6b79371ed367d0140e7
- https://dsf.dev/operations/v2.1.0/bpe/oidc.html
- https://dsf.dev/operations/v2.1.0/fhir/oidc.html
- https://github.com/datasharingframework/dsf
