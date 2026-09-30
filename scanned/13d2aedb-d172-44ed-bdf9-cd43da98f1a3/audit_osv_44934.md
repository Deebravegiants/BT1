# [C] Traefik v3.7.0 Authentication Bypass via from-to-www-redirect

## Summary
Severity: Critical
Advisory: CVE-2026-88877
Aliases: GHSA-cjr6-pf59-jq29
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-09-10
Source: https://osv.dev/vulnerability/CVE-2026-88877
Type: osv

## Details
Traefik is a HTTP reverse proxy and load balancer. In versions >= v3.7.0 and <= v3.7.11, the Kubernetes ingress-nginx provider mishandles Ingresses that carry both an authentication annotation and the nginx.ingress.kubernetes.io/from-to-www-redirect annotation. For such Ingresses the provider creates an additional 'sibling' router that matches on the host alone, carries only the RedirectRegex middleware, and still points at the parent router's protected backend service. Because RedirectRegex is not a terminal handler, a request its pattern does not match is forwarded to the backend, and because the redirect pattern only accepts a numeric port while Traefik's host matcher canonicalizes the authority via net.SplitHostPort, a request with a non-numeric or empty port (for example 'Host: www.example.com:x') selects the sibling router, misses the redirect, and is proxied to the protected backend with none of the Ingress's annotation-derived middlewares applied. This discards not only authentication (e.g. BasicAuth) but every annotation-derived middleware, including source-IP allowlisting. Traefik v2 and v3 releases before v3.7.0 are not affected. The issue is fixed in v3.7.12.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/88xxx/CVE-2026-88877.json
- https://github.com/traefik/traefik/security/advisories/GHSA-cjr6-pf59-jq29
- https://nvd.nist.gov/vuln/detail/CVE-2026-88877
- https://www.vulncheck.com/advisories/traefik-3.7.0-authentication-bypass-via-from-to-www-redirect
