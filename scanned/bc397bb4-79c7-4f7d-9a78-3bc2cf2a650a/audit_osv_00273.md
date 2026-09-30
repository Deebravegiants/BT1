# [M] ALPINE-CVE-2016-8909

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2016-8909
Ecosystem: Alpine:v3.10, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 6.0 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:C/C:N/I:N/A:H)
Published: 2016-11-04
Source: https://osv.dev/vulnerability/ALPINE-CVE-2016-8909
Type: osv

## Affected
- Alpine:v3.10: `qemu` — affected >=0 <2.8.1-r1
- Alpine:v3.6: `qemu` — affected >=0 <2.8.1-r1
- Alpine:v3.7: `qemu` — affected >=0 <2.8.1-r1
- Alpine:v3.8: `qemu` — affected >=0 <2.8.1-r1
- Alpine:v3.9: `qemu` — affected >=0 <2.8.1-r1

## Details
The intel_hda_xfer function in hw/audio/intel-hda.c in QEMU (aka Quick Emulator) allows local guest OS administrators to cause a denial of service (infinite loop and CPU consumption) via an entry with the same value for buffer length and pointer position.

## References
- https://security.alpinelinux.org/vuln/CVE-2016-8909
