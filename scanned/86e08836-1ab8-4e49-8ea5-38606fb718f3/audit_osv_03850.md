# [M] ALPINE-CVE-2026-56434

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2026-56434
Ecosystem: Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:N/VI:L/VA:H/SC:N/SI:N/SA:N/E:X/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X)
Published: 2026-07-15
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-56434
Type: osv

## Affected
- Alpine:v3.21: `nginx` — affected >=0 <1.26.3-r2
- Alpine:v3.22: `nginx` — affected >=0 <1.28.3-r6
- Alpine:v3.23: `nginx` — affected >=0 <1.28.3-r6
- Alpine:v3.24: `nginx` — affected >=0 <1.30.4-r0

## Details
NGINX Plus and NGINX Open Source have a vulnerability in the ngx_http_ssi_module module. This vulnerability may exist when the Server-Side Includes (SSI), proxy_pass, and proxy_buffering off directives are configured. With this configuration, an unauthenticated attacker with man-in-the-middle (MITM) ability to control responses from an upstream server may be able to cause a use-after-free in the NGINX worker process. This issue may lead to limited modification of memory or a restart of the NGINX worker process.

Impact:
This vulnerability may allow remote attackers to have limited control to modify memory contents or restart the NGINX worker process. There is no control plane exposure; this is a data plane issue only.

Note: Software versions which have reached End of Technical Support (EoTS) are not evaluated.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-56434
