# [M] NGINX ngx_http_ssl_module vulnerability

## Summary
Severity: Medium
Advisory: BIT-nginx-2026-40701
Aliases: BIT-nginx-gateway-2026-40701, CVE-2026-40701
Ecosystem: Bitnami
Published: 2026-05-15
Source: https://osv.dev/vulnerability/BIT-nginx-2026-40701
Type: osv

## Affected
- Bitnami: `nginx` — affected >=1.19.0 <1.30.1

## Details
NGINX Plus and NGINX Open Source have a vulnerability in the ngx_http_ssl_module module when the ssl_verify_client directive is set to "on" or "optional," and the ssl_ocsp directive is set to "on" or the leaf parameters are configured with a resolver. With this configuration, an unauthenticated attacker can send requests along with conditions beyond its control that may cause a heap-use-after-free error in the NGINX worker process. This vulnerability may result in limited modification of data or the NGINX worker process restarting.



 Note: Software versions which have reached End of Technical Support (EoTS) are not evaluated.

## References
- https://my.f5.com/manage/s/article/K000161021
- https://nvd.nist.gov/vuln/detail/CVE-2026-40701
