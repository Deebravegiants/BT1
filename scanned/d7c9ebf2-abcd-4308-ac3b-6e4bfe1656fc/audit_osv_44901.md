# [H] Traefik HTTP/3 Backend NTLM Connection Reuse

## Summary
Severity: High
Advisory: CVE-2026-88007
Aliases: GHSA-qqjf-53cj-pwvv
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-09-10
Source: https://osv.dev/vulnerability/CVE-2026-88007
Type: osv

## Details
Traefik is an open source HTTP reverse proxy and load balancer. From 2.11.0 until 2.11.57 and 3.7.13, the HTTP/3 entrypoint ConnContext does not call service.AddTransportOnContext, so kerberosRoundTripper uses a shared backend transport instead of a transport dedicated to each frontend connection. With HTTP/3 enabled, a backend using connection-bound NTLM or Negotiate authentication, and backend keep-alive, an unrelated client can reuse a backend connection authenticated for a victim, read victim-only data, and act as that victim without the victim credentials. This issue is fixed in 2.11.57 and 3.7.13.

## References
- https://github.com/traefik/traefik/releases/tag/v2.11.57
- https://github.com/traefik/traefik/releases/tag/v3.7.13
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/88xxx/CVE-2026-88007.json
- https://github.com/traefik/traefik/security/advisories/GHSA-qqjf-53cj-pwvv
- https://nvd.nist.gov/vuln/detail/CVE-2026-88007
- https://github.com/traefik/traefik/commit/ff39c47d7459dec9cd8de63c1a4e7aa7315bdc1c
- https://github.com/traefik/traefik/pull/13812
