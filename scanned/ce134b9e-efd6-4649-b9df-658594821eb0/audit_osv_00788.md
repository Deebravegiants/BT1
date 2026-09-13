# [C] ALPINE-CVE-2017-8807

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2017-8807
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.3, Alpine:v3.4, Alpine:v3.5, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2017-11-16
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-8807
Type: osv

## Affected
- Alpine:v3.10: `varnish` — affected >=4.1.0 <5.2.1-r0
- Alpine:v3.11: `varnish` — affected >=4.1.0 <5.2.1-r0
- Alpine:v3.12: `varnish` — affected >=4.1.0 <5.2.1-r0
- Alpine:v3.13: `varnish` — affected >=4.1.0 <5.2.1-r0
- Alpine:v3.14: `varnish` — affected >=4.1.0 <5.2.1-r0
- Alpine:v3.15: `varnish` — affected >=4.1.0 <5.2.1-r0
- Alpine:v3.16: `varnish` — affected >=4.1.0 <5.2.1-r0
- Alpine:v3.17: `varnish` — affected >=4.1.0 <5.2.1-r0
- Alpine:v3.18: `varnish` — affected >=4.1.0 <5.2.1-r0
- Alpine:v3.19: `varnish` — affected >=4.1.0 <5.2.1-r0
- Alpine:v3.20: `varnish` — affected >=4.1.0 <5.2.1-r0
- Alpine:v3.21: `varnish` — affected >=4.1.0 <5.2.1-r0
- Alpine:v3.22: `varnish` — affected >=4.1.0 <5.2.1-r0
- Alpine:v3.23: `varnish` — affected >=4.1.0 <5.2.1-r0
- Alpine:v3.24: `varnish` — affected >=4.1.0 <5.2.1-r0
- Alpine:v3.3: `varnish` — affected >=4.1.0 <4.1.9-r0
- Alpine:v3.4: `varnish` — affected >=4.1.0 <4.1.9-r0
- Alpine:v3.5: `varnish` — affected >=4.1.0 <4.1.9-r0
- Alpine:v3.6: `varnish` — affected >=4.1.0 <4.1.9-r0
- Alpine:v3.7: `varnish` — affected >=4.1.0 <5.2.1-r0
- Alpine:v3.8: `varnish` — affected >=4.1.0 <5.2.1-r0
- Alpine:v3.9: `varnish` — affected >=4.1.0 <5.2.1-r0

## Details
vbf_stp_error in bin/varnishd/cache/cache_fetch.c in Varnish HTTP Cache 4.1.x before 4.1.9 and 5.x before 5.2.1 allows remote attackers to obtain sensitive information from process memory because a VFP_GetStorage buffer is larger than intended in certain circumstances involving -sfile Stevedore transient objects.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-8807
