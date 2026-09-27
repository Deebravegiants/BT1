# [M] Data Sharing Framework has an Inverted Time Comparison in OIDC JWKS and Token Cache

## Summary
Severity: Medium
Advisory: GHSA-xmj9-7625-f634
CVE: CVE-2026-40942
CWE: CWE-670
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:N/VI:N/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-04-15
Source: https://github.com/advisories/GHSA-xmj9-7625-f634
Type: github-advisory

## Affected
- Maven: `dev.dsf:dsf-bpe-process-api-v2` — affected >=0
- Maven: `dev.dsf:dsf-bpe-server` — affected >=0

## Details
### Affected Components
- DSF FHIR Server with enabled [bearer-token authentication](https://dsf.dev/operations/v2.1.0/fhir/oidc.html) or [back-channel logout](https://dsf.dev/operations/v2.1.0/fhir/oidc.html).
- DSF BPE Server with enabled [bearer-token authentication](https://dsf.dev/operations/v2.1.0/bpe/oidc.html) or [back-channel logout](https://dsf.dev/operations/v2.1.0/bpe/oidc.html).
- DSF BPE Server API v2 process plugins using [FHIR client connections](https://dsf.dev/operations/v2.1.0/bpe/fhir-client-connections.html) with configured OIDC authentication.

### Summary
- The OIDC JWKS and Metadata Document caches used an inverted time comparison (`isBefore` instead of `isAfter`), causing the cache to **never return cached values**. Every incoming request triggered a fresh HTTP fetch of the OIDC Metadata Document and JWKS keys from the OIDC provider.
- The OIDC token cache for the [FHIR client connections](https://dsf.dev/operations/v2.1.0/bpe/fhir-client-connections.html) used an inverted time comparison (`isBefore` instead of `isAfter`), causing the cache to **never invalidate**. Every incoming request returned the same OIDC token even if expired.

### Impact
- **Performance:** Every OIDC-authenticated request added network round-trips to the OIDC provider, increasing latency
- **Reliability:** Cached OIDC tokens become unusable after expiration and can only be invalidated by restart of the BPE. 
 If the OIDC provider is temporarily unreachable, all requests fail immediately instead of using cached keys
- **Load:** Unnecessary load on the OIDC provider, potentially causing rate limiting

### Fix (commits 31c2e974d, d3ca59b4d)
- Fixed cache timeout comparison from `isBefore` to `isAfter` in `BaseOidcClientWithCache` (configuration and JWKS caches) and `OidcClientWithCache` (configuration, JWKS, and access token caches)
- Added configurable cache timeouts via `dev.dsf.server.auth.oidc.provider.client.cache.timeout.configuration.resource` and `dev.dsf.server.auth.oidc.provider.client.cache.timeout.jwks.resource` (default: `PT1H`)

## References
- https://github.com/datasharingframework/dsf/security/advisories/GHSA-xmj9-7625-f634
- https://nvd.nist.gov/vuln/detail/CVE-2026-40942
- https://github.com/datasharingframework/dsf/commit/31c2e974dfd4351756104ee8c53dbcd666192fef
- https://github.com/datasharingframework/dsf/commit/d3ca59b4daccde16a006fedeccce28fd1f826908
- https://github.com/datasharingframework/dsf
