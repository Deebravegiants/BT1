# [M] ALPINE-CVE-2024-7347

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2024-7347
Ecosystem: Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 4.7 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-08-14
Source: https://osv.dev/vulnerability/ALPINE-CVE-2024-7347
Type: osv

## Affected
- Alpine:v3.20: `nginx` — affected >=0 <1.26.2-r0
- Alpine:v3.21: `nginx` — affected >=0 <1.26.2-r0
- Alpine:v3.22: `nginx` — affected >=0 <1.26.2-r0
- Alpine:v3.23: `nginx` — affected >=0 <1.26.2-r0
- Alpine:v3.24: `nginx` — affected >=0 <1.26.2-r0

## Details
NGINX Open Source and NGINX Plus have a vulnerability in the ngx_http_mp4_module, which might allow an attacker to over-read NGINX worker memory resulting in its termination, using a specially crafted mp4 file. The issue only affects NGINX if it is built with the ngx_http_mp4_module and the mp4 directive is used in the configuration file. Additionally, the attack is possible only if an attacker can trigger the processing of a specially crafted mp4 file with the ngx_http_mp4_module.  Note: Software versions which have reached End of Technical Support (EoTS) are not evaluated.

## References
- https://security.alpinelinux.org/vuln/CVE-2024-7347
