# [M] TLS Session Resumption Vulnerability

## Summary
Severity: Medium
Advisory: BIT-nginx-2025-23419
Aliases: BIT-nginx-gateway-2025-23419, CVE-2025-23419
Ecosystem: Bitnami
Published: 2025-02-07
Source: https://osv.dev/vulnerability/BIT-nginx-2025-23419
Type: osv

## Affected
- Bitnami: `nginx` — affected >=1.27.0 <1.27.4

## Details
When multiple server blocks are configured to share the same IP address and port, an attacker can use session resumption to bypass client certificate authentication requirements on these servers. This vulnerability arises when  TLS Session Tickets https://nginx.org/en/docs/http/ngx_http_ssl_module.html#ssl_session_ticket_key  are used and/or the  SSL session cache https://nginx.org/en/docs/http/ngx_http_ssl_module.html#ssl_session_cache  are used in the default server and the default server is performing client certificate authentication.  

Note: Software versions which have reached End of Technical Support (EoTS) are not evaluated.

## References
- https://my.f5.com/manage/s/article/K000149173
- http://www.openwall.com/lists/oss-security/2025/02/05/8
- https://nvd.nist.gov/vuln/detail/CVE-2025-23419
- https://lists.debian.org/debian-lts-announce/2025/03/msg00017.html
