# [H] ALPINE-CVE-2022-41741

## Summary
Severity: High
Advisory: ALPINE-CVE-2022-41741
Ecosystem: Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-10-19
Source: https://osv.dev/vulnerability/ALPINE-CVE-2022-41741
Type: osv

## Affected
- Alpine:v3.16: `nginx` — affected >=1.1.3 <1.22.1-r0
- Alpine:v3.17: `nginx` — affected >=1.1.3 <1.22.1-r0
- Alpine:v3.18: `nginx` — affected >=1.1.3 <1.22.1-r0
- Alpine:v3.19: `nginx` — affected >=1.1.3 <1.22.1-r0
- Alpine:v3.20: `nginx` — affected >=1.1.3 <1.22.1-r0
- Alpine:v3.21: `nginx` — affected >=1.1.3 <1.22.1-r0
- Alpine:v3.22: `nginx` — affected >=1.1.3 <1.22.1-r0
- Alpine:v3.23: `nginx` — affected >=1.1.3 <1.22.1-r0
- Alpine:v3.24: `nginx` — affected >=1.1.3 <1.22.1-r0

## Details
NGINX Open Source before versions 1.23.2 and 1.22.1, NGINX Open Source Subscription before versions R2 P1 and R1 P1, and NGINX Plus before versions R27 P1 and R26 P1 have a vulnerability in the module ngx_http_mp4_module that might allow a local attacker to corrupt NGINX worker memory, resulting in its termination or potential other impact using a specially crafted audio or video file. The issue affects only NGINX products that are built with the ngx_http_mp4_module, when the mp4 directive is used in the configuration file. Further, the attack is possible only if an attacker can trigger processing of a specially crafted audio or video file with the module ngx_http_mp4_module.

## References
- https://security.alpinelinux.org/vuln/CVE-2022-41741
