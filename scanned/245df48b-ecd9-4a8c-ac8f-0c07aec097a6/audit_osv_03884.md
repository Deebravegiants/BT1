# [H] ALPINE-CVE-2026-60005

## Summary
Severity: High
Advisory: ALPINE-CVE-2026-60005
Ecosystem: Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 8.2 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:H)
Published: 2026-07-15
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-60005
Type: osv

## Affected
- Alpine:v3.21: `nginx` — affected >=0 <1.26.3-r2
- Alpine:v3.22: `nginx` — affected >=0 <1.28.3-r6
- Alpine:v3.23: `nginx` — affected >=0 <1.28.3-r6
- Alpine:v3.24: `nginx` — affected >=0 <1.30.4-r0

## Details
NGINX Plus and NGINX Open Source have a vulnerability in the ngx_http_slice_module module. When the slice directive and unnamed regex captures are configured or when a background cache update happens, unauthenticated attackers can send requests that may cause uninitialized memory access in the NGINX worker process, leading to limited disclosure of memory or a restart.

Impact:
This vulnerability may allow remote, unauthenticated attackers to have limited control to disclose memory contents or restart the NGINX worker process. There is no control plane exposure; this is a data plane issue only.
Note: The ngx_http_slice_module module is not enabled by default; it's enabled with the --with-http_slice_module configuration parameter.

Note: Software versions which have reached End of Technical Support (EoTS) are not evaluated.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-60005
