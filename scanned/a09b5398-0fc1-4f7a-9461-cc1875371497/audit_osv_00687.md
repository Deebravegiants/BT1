# [H] ALPINE-CVE-2017-5931

## Summary
Severity: High
Advisory: ALPINE-CVE-2017-5931
Ecosystem: Alpine:v3.10, Alpine:v3.5, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 8.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2017-03-27
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-5931
Type: osv

## Affected
- Alpine:v3.10: `qemu` — affected >=0 <2.8.1-r1
- Alpine:v3.5: `qemu` — affected >=0 <2.8.1.1-r0
- Alpine:v3.6: `qemu` — affected >=0 <2.8.1-r1
- Alpine:v3.7: `qemu` — affected >=0 <2.8.1-r1
- Alpine:v3.8: `qemu` — affected >=0 <2.8.1-r1
- Alpine:v3.9: `qemu` — affected >=0 <2.8.1-r1

## Details
Integer overflow in hw/virtio/virtio-crypto.c in QEMU (aka Quick Emulator) allows local guest OS privileged users to cause a denial of service (QEMU process crash) or possibly execute arbitrary code on the host via a crafted virtio-crypto request, which triggers a heap-based buffer overflow.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-5931
