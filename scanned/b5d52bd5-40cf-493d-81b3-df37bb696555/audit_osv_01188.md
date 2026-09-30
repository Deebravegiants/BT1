# [M] ALPINE-CVE-2018-5244

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2018-5244
Ecosystem: Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 6.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:C/C:N/I:N/A:H)
Published: 2018-01-05
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-5244
Type: osv

## Affected
- Alpine:v3.15: `xen` — affected >=4.10.0 <4.10.0-r1
- Alpine:v3.16: `xen` — affected >=4.10.0 <4.10.0-r1
- Alpine:v3.17: `xen` — affected >=4.10.0 <4.10.0-r1
- Alpine:v3.18: `xen` — affected >=4.10.0 <4.10.0-r1
- Alpine:v3.19: `xen` — affected >=4.10.0 <4.10.0-r1
- Alpine:v3.20: `xen` — affected >=4.10.0 <4.10.0-r1
- Alpine:v3.21: `xen` — affected >=4.10.0 <4.10.0-r1
- Alpine:v3.22: `xen` — affected >=4.10.0 <4.10.0-r1
- Alpine:v3.23: `xen` — affected >=4.10.0 <4.10.0-r1
- Alpine:v3.24: `xen` — affected >=4.10.0 <4.10.0-r1

## Details
In Xen 4.10, new infrastructure was introduced as part of an overhaul to how MSR emulation happens for guests. Unfortunately, one tracking structure isn't freed when a vcpu is destroyed. This allows guest OS administrators to cause a denial of service (host OS memory consumption) by rebooting many times.

## References
- https://security.alpinelinux.org/vuln/CVE-2018-5244
