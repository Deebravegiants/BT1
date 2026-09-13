# [M] ALPINE-CVE-2020-25597

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2020-25597
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.9
CVSS: 6.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:N/I:N/A:H)
Published: 2020-09-23
Source: https://osv.dev/vulnerability/ALPINE-CVE-2020-25597
Type: osv

## Affected
- Alpine:v3.10: `xen` — affected >=4.4.0 <4.12.3-r4
- Alpine:v3.11: `xen` — affected >=4.4.0 <4.13.1-r4
- Alpine:v3.12: `xen` — affected >=4.4.0 <4.13.1-r4
- Alpine:v3.13: `xen` — affected >=4.4.0 <4.14.0-r1
- Alpine:v3.14: `xen` — affected >=4.4.0 <4.14.0-r1
- Alpine:v3.15: `xen` — affected >=4.4.0 <4.14.0-r1
- Alpine:v3.16: `xen` — affected >=4.4.0 <4.14.0-r1
- Alpine:v3.17: `xen` — affected >=4.4.0 <4.14.0-r1
- Alpine:v3.18: `xen` — affected >=4.4.0 <4.14.0-r1
- Alpine:v3.19: `xen` — affected >=4.4.0 <4.14.0-r1
- Alpine:v3.20: `xen` — affected >=4.4.0 <4.14.0-r1
- Alpine:v3.21: `xen` — affected >=4.4.0 <4.14.0-r1
- Alpine:v3.22: `xen` — affected >=4.4.0 <4.14.0-r1
- Alpine:v3.23: `xen` — affected >=4.4.0 <4.14.0-r1
- Alpine:v3.24: `xen` — affected >=4.4.0 <4.14.0-r1
- Alpine:v3.9: `xen` — affected >=4.4.0 <4.11.4-r2

## Details
An issue was discovered in Xen through 4.14.x. There is mishandling of the constraint that once-valid event channels may not turn invalid. Logic in the handling of event channel operations in Xen assumes that an event channel, once valid, will not become invalid over the life time of a guest. However, operations like the resetting of all event channels may involve decreasing one of the bounds checked when determining validity. This may lead to bug checks triggering, crashing the host. An unprivileged guest may be able to crash Xen, leading to a Denial of Service (DoS) for the entire system. All Xen versions from 4.4 onwards are vulnerable. Xen versions 4.3 and earlier are not vulnerable. Only systems with untrusted guests permitted to create more than the default number of event channels are vulnerable. This number depends on the architecture and type of guest. For 32-bit x86 PV guests, this is 1023; for 64-bit x86 PV guests, and for all ARM guests, this number is 4095. Systems where untrusted guests are limited to fewer than this number are not vulnerable. Note that xl and libxl limit max_event_channels to 1023 by default, so systems using exclusively xl, libvirt+libxl, or their own toolstack based on libxl, and not explicitly setting max_event_channels, are not vulnerable.

## References
- https://security.alpinelinux.org/vuln/CVE-2020-25597
