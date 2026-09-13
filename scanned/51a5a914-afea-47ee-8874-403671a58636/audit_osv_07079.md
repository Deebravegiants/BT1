# [M] NGINX ngx_http_proxy_v2_module vulnerability

## Summary
Severity: Medium
Advisory: BIT-nginx-2026-42926
Aliases: BIT-nginx-gateway-2026-42926, CVE-2026-42926
Ecosystem: Bitnami
Published: 2026-05-15
Source: https://osv.dev/vulnerability/BIT-nginx-2026-42926
Type: osv

## Affected
- Bitnami: `nginx` — affected >=1.29.4 <1.30.1

## Details
When NGINX Open Source is configured to proxy HTTP/2 traffic by setting proxy_http_version to 2, and also uses proxy_set_body, an attacker may be able to inject frame headers and payload bytes to the upstream peer.  Note: Software versions which have reached End of Technical Support (EoTS) are not evaluated.

## References
- https://my.f5.com/manage/s/article/K000161131
- https://nvd.nist.gov/vuln/detail/CVE-2026-42926
