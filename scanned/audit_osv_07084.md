# [H] NGINX ngx_http_ssi_module vulnerability

## Summary
Severity: High
Advisory: BIT-nginx-2026-56434
Aliases: BIT-nginx-gateway-2026-56434, CVE-2026-56434
Ecosystem: Bitnami
Published: 2026-07-20
Source: https://osv.dev/vulnerability/BIT-nginx-2026-56434
Type: osv

## Affected
- Bitnami: `nginx` — affected >=1.31.0 <1.31.3

## Details
NGINX Plus and NGINX Open Source have a vulnerability in the ngx_http_ssi_module module. This vulnerability may exist when the Server-Side Includes (SSI), proxy_pass, and proxy_buffering off directives are configured. With this configuration, an unauthenticated attacker with man-in-the-middle (MITM) ability to control responses from an upstream server may be able to cause a use-after-free in the NGINX worker process. This issue may lead to limited modification of memory or a restart of the NGINX worker process.

Impact:
This vulnerability may allow remote attackers to have limited control to modify memory contents or restart the NGINX worker process. There is no control plane exposure; this is a data plane issue only.

Note: Software versions which have reached End of Technical Support (EoTS) are not evaluated.

## References
- https://my.f5.com/manage/s/article/K000162098
- https://nvd.nist.gov/vuln/detail/CVE-2026-56434
