# [H] NGINX ngx_http_slice_module vulnerability

## Summary
Severity: High
Advisory: BIT-nginx-2026-60005
Aliases: BIT-nginx-gateway-2026-60005, CVE-2026-60005
Ecosystem: Bitnami
Published: 2026-07-20
Source: https://osv.dev/vulnerability/BIT-nginx-2026-60005
Type: osv

## Affected
- Bitnami: `nginx` — affected >=1.31.0 <1.31.3

## Details
NGINX Plus and NGINX Open Source have a vulnerability in the ngx_http_slice_module module. When the slice directive and unnamed regex captures are configured or when a background cache update happens, unauthenticated attackers can send requests that may cause uninitialized memory access in the NGINX worker process, leading to limited disclosure of memory or a restart.

Impact:
This vulnerability may allow remote, unauthenticated attackers to have limited control to disclose memory contents or restart the NGINX worker process. There is no control plane exposure; this is a data plane issue only.
Note: The ngx_http_slice_module module is not enabled by default; it's enabled with the --with-http_slice_module configuration parameter.

Note: Software versions which have reached End of Technical Support (EoTS) are not evaluated.

## References
- https://my.f5.com/manage/s/article/K000162100
- https://nvd.nist.gov/vuln/detail/CVE-2026-60005
