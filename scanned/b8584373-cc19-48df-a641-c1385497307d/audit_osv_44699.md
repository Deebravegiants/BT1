# [M] Traefik v3.7.1 crossProviderNamespaces Bypass via Service Middleware

## Summary
Severity: Medium
Advisory: CVE-2026-85594
Aliases: GHSA-m6wx-622r-48r9
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:N/VC:H/VI:N/VA:N/SC:H/SI:N/SA:N)
Published: 2026-09-04
Source: https://osv.dev/vulnerability/CVE-2026-85594
Type: osv

## Details
Traefik versions from v3.7.1 fail to enforce crossProviderNamespaces restrictions on the traefik.ingress.kubernetes.io/service.middlewares Service annotation in the Kubernetes Ingress provider. A namespace-limited tenant excluded from the allowlist can attach an operator-owned middleware to its Service, and if that middleware injects backend credentials, recover them at a controlled backend.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/85xxx/CVE-2026-85594.json
- https://github.com/traefik/traefik/security/advisories/GHSA-m6wx-622r-48r9
- https://nvd.nist.gov/vuln/detail/CVE-2026-85594
- https://www.vulncheck.com/advisories/traefik-3.7.1-crossprovidernamespaces-bypass-via-service-middleware
