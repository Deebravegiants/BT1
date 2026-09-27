# [M] ALPINE-CVE-2022-26356

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2022-26356
Ecosystem: Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.6 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:C/C:N/I:N/A:H)
Published: 2022-04-05
Source: https://osv.dev/vulnerability/ALPINE-CVE-2022-26356
Type: osv

## Affected
- Alpine:v3.12: `xen` — affected >=4.0.0 <4.13.4-r3
- Alpine:v3.13: `xen` — affected >=4.0.0 <4.14.5-r0
- Alpine:v3.14: `xen` — affected >=4.0.0 <4.15.2-r2
- Alpine:v3.15: `xen` — affected >=4.0.0 <4.15.2-r2
- Alpine:v3.16: `xen` — affected >=4.0.0 <4.16.1-r0
- Alpine:v3.17: `xen` — affected >=4.0.0 <4.16.1-r0
- Alpine:v3.18: `xen` — affected >=4.0.0 <4.16.1-r0
- Alpine:v3.19: `xen` — affected >=4.0.0 <4.16.1-r0
- Alpine:v3.20: `xen` — affected >=4.0.0 <4.16.1-r0
- Alpine:v3.21: `xen` — affected >=4.0.0 <4.16.1-r0
- Alpine:v3.22: `xen` — affected >=4.0.0 <4.16.1-r0
- Alpine:v3.23: `xen` — affected >=4.0.0 <4.16.1-r0
- Alpine:v3.24: `xen` — affected >=4.0.0 <4.16.1-r0

## Details
Racy interactions between dirty vram tracking and paging log dirty hypercalls Activation of log dirty mode done by XEN_DMOP_track_dirty_vram (was named HVMOP_track_dirty_vram before Xen 4.9) is racy with ongoing log dirty hypercalls. A suitably timed call to XEN_DMOP_track_dirty_vram can enable log dirty while another CPU is still in the process of tearing down the structures related to a previously enabled log dirty mode (XEN_DOMCTL_SHADOW_OP_OFF). This is due to lack of mutually exclusive locking between both operations and can lead to entries being added in already freed slots, resulting in a memory leak.

## References
- https://security.alpinelinux.org/vuln/CVE-2022-26356
