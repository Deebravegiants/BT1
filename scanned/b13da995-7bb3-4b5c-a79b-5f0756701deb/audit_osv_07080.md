# [M] NGINX ngx_http_charset_module vulnerability

## Summary
Severity: Medium
Advisory: BIT-nginx-2026-42934
Aliases: BIT-nginx-gateway-2026-42934, CVE-2026-42934
Ecosystem: Bitnami
Published: 2026-05-15
Source: https://osv.dev/vulnerability/BIT-nginx-2026-42934
Type: osv

## Affected
- Bitnami: `nginx` — affected >=0.3.50 <1.30.1

## Details
NGINX Plus and NGINX Open Source have a vulnerability in the ngx_http_charset_module module. When charset, source_charset, and charset_map and proxy_pass with disabled buffering ("off") directives are configured, unauthenticated attackers can send requests that with conditions beyond the attackers' control to cause a heap buffer over-read in the NGINX worker process, leading to limited disclosure of memory or a restart.



 Note: Software versions which have reached End of Technical Support (EoTS) are not evaluated.

## References
- https://my.f5.com/manage/s/article/K000161028
- https://nvd.nist.gov/vuln/detail/CVE-2026-42934
