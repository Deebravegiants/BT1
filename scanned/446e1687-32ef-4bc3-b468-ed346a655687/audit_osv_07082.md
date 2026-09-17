# [H] NGINX ngx_http_scgi_module and ngx_http_uwsgi_module vulnerability

## Summary
Severity: High
Advisory: BIT-nginx-2026-42946
Aliases: BIT-nginx-gateway-2026-42946, CVE-2026-42946
Ecosystem: Bitnami
Published: 2026-05-15
Source: https://osv.dev/vulnerability/BIT-nginx-2026-42946
Type: osv

## Affected
- Bitnami: `nginx` — affected >=0.8.42 <1.30.1

## Details
A vulnerability exists in the ngx_http_scgi_module and ngx_http_uwsgi_module modules that may result in excessive memory allocation or an over-read of data. When scgi_pass or uwsgi_pass is configured, an unauthenticated attacker with man-in-the-middle (MITM) ability to control responses from an upstream server may be able to read the memory of the NGINX worker process or restart it.  Note: Software versions which have reached End of Technical Support (EoTS) are not evaluated.

## References
- https://my.f5.com/manage/s/article/K000161027
- https://nvd.nist.gov/vuln/detail/CVE-2026-42946
