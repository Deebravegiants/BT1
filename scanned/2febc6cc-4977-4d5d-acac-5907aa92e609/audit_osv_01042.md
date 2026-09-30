# [M] ALPINE-CVE-2018-16845

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2018-16845
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 6.1 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:L/I:N/A:H)
Published: 2018-11-07
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-16845
Type: osv

## Affected
- Alpine:v3.10: `nginx` — affected >=1.0.7 <1.14.1-r0
- Alpine:v3.11: `nginx` — affected >=1.0.7 <1.14.1-r0
- Alpine:v3.12: `nginx` — affected >=1.0.7 <1.14.1-r0
- Alpine:v3.13: `nginx` — affected >=1.0.7 <1.14.1-r0
- Alpine:v3.14: `nginx` — affected >=1.0.7 <1.14.1-r0
- Alpine:v3.15: `nginx` — affected >=1.0.7 <1.14.1-r0
- Alpine:v3.16: `nginx` — affected >=1.0.7 <1.14.1-r0
- Alpine:v3.17: `nginx` — affected >=1.0.7 <1.14.1-r0
- Alpine:v3.18: `nginx` — affected >=1.0.7 <1.14.1-r0
- Alpine:v3.19: `nginx` — affected >=1.0.7 <1.14.1-r0
- Alpine:v3.20: `nginx` — affected >=1.0.7 <1.14.1-r0
- Alpine:v3.21: `nginx` — affected >=1.0.7 <1.14.1-r0
- Alpine:v3.22: `nginx` — affected >=1.0.7 <1.14.1-r0
- Alpine:v3.23: `nginx` — affected >=1.0.7 <1.14.1-r0
- Alpine:v3.24: `nginx` — affected >=1.0.7 <1.14.1-r0
- Alpine:v3.6: `nginx` — affected >=1.0.7 <1.12.2-r2
- Alpine:v3.7: `nginx` — affected >=1.0.7 <1.12.1-r4
- Alpine:v3.8: `nginx` — affected >=1.0.7 <1.14.1-r0
- Alpine:v3.9: `nginx` — affected >=1.0.7 <1.14.1-r0

## Details
nginx before versions 1.15.6, 1.14.1 has a vulnerability in the ngx_http_mp4_module, which might allow an attacker to cause infinite loop in a worker process, cause a worker process crash, or might result in worker process memory disclosure by using a specially crafted mp4 file. The issue only affects nginx if it is built with the ngx_http_mp4_module (the module is not built by default) and the .mp4. directive is used in the configuration file. Further, the attack is only possible if an attacker is able to trigger processing of a specially crafted mp4 file with the ngx_http_mp4_module.

## References
- https://security.alpinelinux.org/vuln/CVE-2018-16845
