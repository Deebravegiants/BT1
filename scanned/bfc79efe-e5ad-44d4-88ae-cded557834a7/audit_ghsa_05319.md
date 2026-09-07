# [H] Fulcio has OIDC Discovery Redirect Following Allows SSRF and JWKS Substitution for Meta-Issuer Paths, with Kubernetes Service-Account Token Leakage

## Summary
Severity: High
Advisory: GHSA-f5mr-q85p-6hh6
CVE: CVE-2026-49478
CWE: CWE-918
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2026-06-30
Source: https://github.com/advisories/GHSA-f5mr-q85p-6hh6
Type: github-advisory

## Affected
- Go: `github.com/sigstore/fulcio` — affected >=0 <1.8.6

## Details
## Impact

Three security vulnerabilities were identified in the OIDC Discovery client:

1. **Blind Server-Side Request Forgery (SSRF) via Cross-Host Redirects**:
   Fulcio uses an HTTP client to fetch OIDC discovery metadata (`/.well-known/openid-configuration`). Prior to this fix, if a configured issuer returned an HTTP redirect to a different host, the client followed it by default. This allowed a compromised or malicious issuer to redirect Fulcio's discovery requests to internal-only systems, resulting in blind SSRF.

2. **JWKS Substitution and Cache Poisoning**:
   Because cross-host redirects were permitted during OIDC discovery, an attacker could manipulate the discovery flow to return a malicious `jwks_uri` pointing to an attacker-controlled host. When Fulcio successfully initialized the provider and cached the resulting verifier in the verifier cache, it poisoned the cache with the attacker's verification keys. The attacker could then present signatures validated against the poisoned keys.

3. **Kubernetes ServiceAccount Token Leakage**:
   Fulcio mounts an in-cluster Kubernetes ServiceAccount token to authenticate OIDC discovery requests sent to the local control plane API server (`https://kubernetes.default.svc`).
   * **Cross-Host Redirects & JWKS**: The token was previously attached globally by the transport, leaking it to third-party hosts if the issuer performed a redirect or if the `jwks_uri` pointed to a different domain.
   * **Wildcard MetaIssuers**: If a wildcard `MetaIssuer` of type `kubernetes` (e.g., matching external EKS/GKE endpoints) was matched, and a local Kubernetes issuer was present in the config, the transport loaded and attached the local in-cluster ServiceAccount token to outbound requests sent to the external host.

## Patches

The following mitigations have been applied:

* **Blocked Cross-Host Redirects**: A custom callback is configured on all OIDC discovery HTTP clients to reject redirects that attempt to cross the original issuer's host boundary.
* **Restricted Token Injection**: Updated the transport to only attach the ServiceAccount token when the outgoing request's host exactly matches the configured host of the issuer.
* **Restricted Local Token Loading**: Constrained the loader to only load and wrap the transport with the local ServiceAccount token when the target issuer URL exactly matches the private local API server (`https://kubernetes.default.svc`).

## Workarounds

None, upgrade to v1.8.6

## References
- https://github.com/sigstore/fulcio/security/advisories/GHSA-f5mr-q85p-6hh6
- https://github.com/sigstore/fulcio
