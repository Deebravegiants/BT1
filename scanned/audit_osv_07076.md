# [C] NGINX ngx_http_proxy_v2_module and ngx_http_grpc_module vulnerability

## Summary
Severity: Critical
Advisory: BIT-nginx-2026-42055
Aliases: BIT-nginx-gateway-2026-42055, BIT-nginx-gateway-fabric-2026-42055, CVE-2026-42055
Ecosystem: Bitnami
Published: 2026-06-22
Source: https://osv.dev/vulnerability/BIT-nginx-2026-42055
Type: osv

## Affected
- Bitnami: `nginx` — affected >=1.31.0 <1.31.2

## Details
NGINX Plus and NGINX Open Source have a vulnerability in the ngx_http_proxy_v2_module and ngx_http_grpc_module modules. This vulnerability exists when the proxy_http_version to 2 or grpc_pass directives are used to proxy HTTP/2 traffic, the ignore_invalid_headers directive is set to off, and the large_client_header_buffers directive size is larger than 2 megabytes. A remote, unauthenticated attacker, along with conditions beyond their control, could send large headers while creating an upstream request. This may cause a heap-based buffer overflow in the NGINX worker process leading to a restart. Additionally, attackers can execute code on systems with Address Space Layout Randomization (ASLR) disabled or when the attacker can bypass ASLR. 


Note: Software versions which have reached End of Technical Support (EoTS) are not evaluated.

## References
- https://my.f5.com/manage/s/article/K000161584
- https://nvd.nist.gov/vuln/detail/CVE-2026-42055
- https://access.redhat.com/errata/RHSA-2026:27197
- https://access.redhat.com/security/cve/CVE-2026-42055
- https://bugzilla.redhat.com/show_bug.cgi?id=2489866
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-42055.json
- https://access.redhat.com/errata/RHSA-2026:36331
- https://access.redhat.com/errata/RHSA-2026:36364
- https://access.redhat.com/errata/RHSA-2026:36618
- https://access.redhat.com/errata/RHSA-2026:36639
- https://access.redhat.com/errata/RHSA-2026:38847
- https://access.redhat.com/errata/RHSA-2026:44481
- https://access.redhat.com/errata/RHSA-2026:46836
- https://access.redhat.com/errata/RHSA-2026:58981
