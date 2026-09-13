# [M] ALPINE-CVE-2020-25601

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2020-25601
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.9
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-09-23
Source: https://osv.dev/vulnerability/ALPINE-CVE-2020-25601
Type: osv

## Affected
- Alpine:v3.10: `xen` — affected >=0 <4.12.3-r4
- Alpine:v3.11: `xen` — affected >=0 <4.13.1-r4
- Alpine:v3.12: `xen` — affected >=0 <4.13.1-r4
- Alpine:v3.13: `xen` — affected >=0 <4.14.0-r1
- Alpine:v3.14: `xen` — affected >=0 <4.14.0-r1
- Alpine:v3.15: `xen` — affected >=0 <4.14.0-r1
- Alpine:v3.16: `xen` — affected >=0 <4.14.0-r1
- Alpine:v3.17: `xen` — affected >=0 <4.14.0-r1
- Alpine:v3.18: `xen` — affected >=0 <4.14.0-r1
- Alpine:v3.19: `xen` — affected >=0 <4.14.0-r1
- Alpine:v3.20: `xen` — affected >=0 <4.14.0-r1
- Alpine:v3.21: `xen` — affected >=0 <4.14.0-r1
- Alpine:v3.22: `xen` — affected >=0 <4.14.0-r1
- Alpine:v3.23: `xen` — affected >=0 <4.14.0-r1
- Alpine:v3.24: `xen` — affected >=0 <4.14.0-r1
- Alpine:v3.9: `xen` — affected >=0 <4.11.4-r2

## Details
An issue was discovered in Xen through 4.14.x. There is a lack of preemption in evtchn_reset() / evtchn_destroy(). In particular, the FIFO event channel model allows guests to have a large number of event channels active at a time. Closing all of these (when resetting all event channels or when cleaning up after the guest) may take extended periods of time. So far, there was no arrangement for preemption at suitable intervals, allowing a CPU to spend an almost unbounded amount of time in the processing of these operations. Malicious or buggy guest kernels can mount a Denial of Service (DoS) attack affecting the entire system. All Xen versions are vulnerable in principle. Whether versions 4.3 and older are vulnerable depends on underlying hardware characteristics.

## References
- https://security.alpinelinux.org/vuln/CVE-2020-25601
