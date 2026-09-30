# [M] NGINX ngx_http_charset_module vulnerability

## Summary
Severity: Medium
Advisory: BIT-nginx-2026-48142
Aliases: BIT-nginx-gateway-2026-48142, BIT-nginx-gateway-fabric-2026-48142, CVE-2026-48142
Ecosystem: Bitnami
Published: 2026-06-22
Source: https://osv.dev/vulnerability/BIT-nginx-2026-48142
Type: osv

## Affected
- Bitnami: `nginx` — affected >=1.31.0 <1.31.2

## Details
NGINX Plus and NGINX Open Source have a vulnerability in the ngx_http_charset_module module. When content is served or proxied through a location block with both source_charset utf-8; and a charset directive (for example, charset koi8-r;) configured, remote, unauthenticated attackers can send requests (in conjunction with conditions beyond their control) to cause a heap buffer over-read in the NGINX worker process, leading to limited disclosure of memory or a restart. 


Note: Software versions which have reached End of Technical Support (EoTS) are not evaluated.

## References
- https://my.f5.com/manage/s/article/K000161585
- https://nvd.nist.gov/vuln/detail/CVE-2026-48142
