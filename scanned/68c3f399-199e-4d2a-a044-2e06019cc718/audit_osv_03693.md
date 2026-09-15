# [C] ALPINE-CVE-2026-42055

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2026-42055
Ecosystem: Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 9.0 (CVSS:4.0/AV:N/AC:H/AT:P/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:X/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X)
Published: 2026-06-17
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-42055
Type: osv

## Affected
- Alpine:v3.21: `nginx` — affected >=0 <1.26.3-r2
- Alpine:v3.22: `nginx` — affected >=0 <1.28.3-r4
- Alpine:v3.23: `nginx` — affected >=0 <1.28.3-r4
- Alpine:v3.24: `nginx` — affected >=0 <1.30.3-r0

## Details
NGINX Plus and NGINX Open Source have a vulnerability in the ngx_http_proxy_v2_module and ngx_http_grpc_module modules. This vulnerability exists when the proxy_http_version to 2 or grpc_pass directives are used to proxy HTTP/2 traffic, the ignore_invalid_headers directive is set to off, and the large_client_header_buffers directive size is larger than 2 megabytes. A remote, unauthenticated attacker, along with conditions beyond their control, could send large headers while creating an upstream request. This may cause a heap-based buffer overflow in the NGINX worker process leading to a restart. Additionally, attackers can execute code on systems with Address Space Layout Randomization (ASLR) disabled or when the attacker can bypass ASLR. 


Note: Software versions which have reached End of Technical Support (EoTS) are not evaluated.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-42055
