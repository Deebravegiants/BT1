# [H] ALPINE-CVE-2020-25599

## Summary
Severity: High
Advisory: ALPINE-CVE-2020-25599
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.9
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-09-23
Source: https://osv.dev/vulnerability/ALPINE-CVE-2020-25599
Type: osv

## Affected
- Alpine:v3.10: `xen` — affected >=4.5.0 <4.12.3-r4
- Alpine:v3.11: `xen` — affected >=4.5.0 <4.13.1-r4
- Alpine:v3.12: `xen` — affected >=4.5.0 <4.13.1-r4
- Alpine:v3.13: `xen` — affected >=4.5.0 <4.14.0-r1
- Alpine:v3.14: `xen` — affected >=4.5.0 <4.14.0-r1
- Alpine:v3.15: `xen` — affected >=4.5.0 <4.14.0-r1
- Alpine:v3.16: `xen` — affected >=4.5.0 <4.14.0-r1
- Alpine:v3.17: `xen` — affected >=4.5.0 <4.14.0-r1
- Alpine:v3.18: `xen` — affected >=4.5.0 <4.14.0-r1
- Alpine:v3.19: `xen` — affected >=4.5.0 <4.14.0-r1
- Alpine:v3.20: `xen` — affected >=4.5.0 <4.14.0-r1
- Alpine:v3.21: `xen` — affected >=4.5.0 <4.14.0-r1
- Alpine:v3.22: `xen` — affected >=4.5.0 <4.14.0-r1
- Alpine:v3.23: `xen` — affected >=4.5.0 <4.14.0-r1
- Alpine:v3.24: `xen` — affected >=4.5.0 <4.14.0-r1
- Alpine:v3.9: `xen` — affected >=4.5.0 <4.11.4-r2

## Details
An issue was discovered in Xen through 4.14.x. There are evtchn_reset() race conditions. Uses of EVTCHNOP_reset (potentially by a guest on itself) or XEN_DOMCTL_soft_reset (by itself covered by XSA-77) can lead to the violation of various internal assumptions. This may lead to out of bounds memory accesses or triggering of bug checks. In particular, x86 PV guests may be able to elevate their privilege to that of the host. Host and guest crashes are also possible, leading to a Denial of Service (DoS). Information leaks cannot be ruled out. All Xen versions from 4.5 onwards are vulnerable. Xen versions 4.4 and earlier are not vulnerable.

## References
- https://security.alpinelinux.org/vuln/CVE-2020-25599
