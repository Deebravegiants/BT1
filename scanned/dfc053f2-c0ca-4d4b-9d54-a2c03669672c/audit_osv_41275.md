# [M] Dapr - OIDC Discovery Issuer and JWKS URI Injection via Unvalidated X-Forwarded-Host

## Summary
Severity: Medium
Advisory: CVE-2026-59096
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-07-02
Source: https://osv.dev/vulnerability/CVE-2026-59096
Type: osv

## Details
Dapr Sentry's OIDC discovery endpoint derives the issuer and jwks_uri of the /.well-known/openid-configuration document from the request Host, honoring an attacker-controlled X-Forwarded-Host header without validation when no allowed-hosts list is configured (the default), and serves the document with a one-hour public cache lifetime. A remote unauthenticated attacker can poison the discovery document so relying parties performing dynamic (unpinned) discovery fetch the JWKS from an attacker-controlled server, causing attacker-signed JWTs to be accepted. Exploitation requires the OIDC server enabled without a configured jwt-issuer or oidc-allowed-hosts.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/59xxx/CVE-2026-59096.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-59096
- https://www.vulncheck.com/advisories/dapr-oidc-discovery-issuer-and-jwks-uri-injection-via-unvalidated-x-forwarded-host
- https://github.com/dapr/dapr/pull/10027
- https://github.com/dapr/dapr/pull/10028
- https://github.com/dapr/dapr/pull/10029
- https://github.com/dapr/dapr
