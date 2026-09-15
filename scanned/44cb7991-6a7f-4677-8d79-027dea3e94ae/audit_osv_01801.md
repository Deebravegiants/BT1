# [M] ALPINE-CVE-2020-15566

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2020-15566
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.9
CVSS: 6.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:N/I:N/A:H)
Published: 2020-07-07
Source: https://osv.dev/vulnerability/ALPINE-CVE-2020-15566
Type: osv

## Affected
- Alpine:v3.10: `xen` — affected >=4.10.0 <4.12.3-r2
- Alpine:v3.11: `xen` — affected >=4.10.0 <4.13.1-r2
- Alpine:v3.12: `xen` — affected >=4.10.0 <4.13.1-r2
- Alpine:v3.13: `xen` — affected >=4.10.0 <4.13.1-r4
- Alpine:v3.14: `xen` — affected >=4.10.0 <4.13.1-r4
- Alpine:v3.15: `xen` — affected >=4.10.0 <4.13.1-r4
- Alpine:v3.16: `xen` — affected >=4.10.0 <4.13.1-r4
- Alpine:v3.17: `xen` — affected >=4.10.0 <4.13.1-r4
- Alpine:v3.18: `xen` — affected >=4.10.0 <4.13.1-r4
- Alpine:v3.19: `xen` — affected >=4.10.0 <4.13.1-r4
- Alpine:v3.20: `xen` — affected >=4.10.0 <4.13.1-r4
- Alpine:v3.21: `xen` — affected >=4.10.0 <4.13.1-r4
- Alpine:v3.22: `xen` — affected >=4.10.0 <4.13.1-r4
- Alpine:v3.23: `xen` — affected >=4.10.0 <4.13.1-r4
- Alpine:v3.24: `xen` — affected >=4.10.0 <4.13.1-r4
- Alpine:v3.9: `xen` — affected >=4.10.0 <4.11.4-r0

## Details
An issue was discovered in Xen through 4.13.x, allowing guest OS users to cause a host OS crash because of incorrect error handling in event-channel port allocation. The allocation of an event-channel port may fail for multiple reasons: (1) port is already in use, (2) the memory allocation failed, or (3) the port we try to allocate is higher than what is supported by the ABI (e.g., 2L or FIFO) used by the guest or the limit set by an administrator (max_event_channels in xl cfg). Due to the missing error checks, only (1) will be considered an error. All the other cases will provide a valid port and will result in a crash when trying to access the event channel. When the administrator configured a guest to allow more than 1023 event channels, that guest may be able to crash the host. When Xen is out-of-memory, allocation of new event channels will result in crashing the host rather than reporting an error. Xen versions 4.10 and later are affected. All architectures are affected. The default configuration, when guests are created with xl/libxl, is not vulnerable, because of the default event-channel limit.

## References
- https://security.alpinelinux.org/vuln/CVE-2020-15566
