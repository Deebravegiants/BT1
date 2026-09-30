# [M] ALPINE-CVE-2017-5578

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2017-5578
Ecosystem: Alpine:v3.10, Alpine:v3.5, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 6.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:N/I:N/A:H)
Published: 2017-03-15
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-5578
Type: osv

## Affected
- Alpine:v3.10: `qemu` — affected >=0 <2.8.1-r1
- Alpine:v3.5: `qemu` — affected >=0 <2.8.1.1-r0
- Alpine:v3.6: `qemu` — affected >=0 <2.8.1-r1
- Alpine:v3.7: `qemu` — affected >=0 <2.8.1-r1
- Alpine:v3.8: `qemu` — affected >=0 <2.8.1-r1
- Alpine:v3.9: `qemu` — affected >=0 <2.8.1-r1

## Details
Memory leak in the virtio_gpu_resource_attach_backing function in hw/display/virtio-gpu.c in QEMU (aka Quick Emulator) allows local guest OS users to cause a denial of service (host memory consumption) via a large number of VIRTIO_GPU_CMD_RESOURCE_ATTACH_BACKING commands.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-5578
