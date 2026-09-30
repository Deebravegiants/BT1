# [H] ALPINE-CVE-2020-29040

## Summary
Severity: High
Advisory: ALPINE-CVE-2020-29040
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 8.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2020-11-24
Source: https://osv.dev/vulnerability/ALPINE-CVE-2020-29040
Type: osv

## Affected
- Alpine:v3.10: `xen` — affected >=0 <4.12.4-r0
- Alpine:v3.11: `xen` — affected >=0 <4.13.2-r2
- Alpine:v3.12: `xen` — affected >=0 <4.13.2-r2
- Alpine:v3.13: `xen` — affected >=0 <4.14.0-r3
- Alpine:v3.14: `xen` — affected >=0 <4.14.0-r3
- Alpine:v3.15: `xen` — affected >=0 <4.14.0-r3
- Alpine:v3.16: `xen` — affected >=0 <4.14.0-r3
- Alpine:v3.17: `xen` — affected >=0 <4.14.0-r3
- Alpine:v3.18: `xen` — affected >=0 <4.14.0-r3
- Alpine:v3.19: `xen` — affected >=0 <4.14.0-r3
- Alpine:v3.20: `xen` — affected >=0 <4.14.0-r3
- Alpine:v3.21: `xen` — affected >=0 <4.14.0-r3
- Alpine:v3.22: `xen` — affected >=0 <4.14.0-r3
- Alpine:v3.23: `xen` — affected >=0 <4.14.0-r3
- Alpine:v3.24: `xen` — affected >=0 <4.14.0-r3

## Details
An issue was discovered in Xen through 4.14.x allowing x86 HVM guest OS users to cause a denial of service (stack corruption), cause a data leak, or possibly gain privileges because of an off-by-one error. NOTE: this issue is caused by an incorrect fix for CVE-2020-27671.

## References
- https://security.alpinelinux.org/vuln/CVE-2020-29040
