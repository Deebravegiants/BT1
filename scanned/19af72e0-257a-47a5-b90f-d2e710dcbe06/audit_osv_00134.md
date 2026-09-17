# [M] ALPINE-CVE-2016-5403

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2016-5403
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.4, Alpine:v3.5, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-08-02
Source: https://osv.dev/vulnerability/ALPINE-CVE-2016-5403
Type: osv

## Affected
- Alpine:v3.10: `xen` — affected >=0 <4.7.0-r0
- Alpine:v3.11: `xen` — affected >=0 <4.7.0-r0
- Alpine:v3.12: `xen` — affected >=0 <4.7.0-r0
- Alpine:v3.13: `xen` — affected >=0 <4.7.0-r0
- Alpine:v3.14: `xen` — affected >=0 <4.7.0-r0
- Alpine:v3.15: `xen` — affected >=0 <4.7.0-r0
- Alpine:v3.16: `xen` — affected >=0 <4.7.0-r0
- Alpine:v3.17: `xen` — affected >=0 <4.7.0-r0
- Alpine:v3.18: `xen` — affected >=0 <4.7.0-r0
- Alpine:v3.19: `xen` — affected >=0 <4.7.0-r0
- Alpine:v3.20: `xen` — affected >=0 <4.7.0-r0
- Alpine:v3.21: `xen` — affected >=0 <4.7.0-r0
- Alpine:v3.22: `xen` — affected >=0 <4.7.0-r0
- Alpine:v3.23: `xen` — affected >=0 <4.7.0-r0
- Alpine:v3.24: `xen` — affected >=0 <4.7.0-r0
- Alpine:v3.4: `xen` — affected >=0 <4.6.3-r1
- Alpine:v3.5: `xen` — affected >=0 <4.7.0-r0
- Alpine:v3.6: `xen` — affected >=0 <4.7.0-r0
- Alpine:v3.7: `xen` — affected >=0 <4.7.0-r0
- Alpine:v3.8: `xen` — affected >=0 <4.7.0-r0
- Alpine:v3.9: `xen` — affected >=0 <4.7.0-r0

## Details
The virtqueue_pop function in hw/virtio/virtio.c in QEMU allows local guest OS administrators to cause a denial of service (memory consumption and QEMU process crash) by submitting requests without waiting for completion.

## References
- https://security.alpinelinux.org/vuln/CVE-2016-5403
