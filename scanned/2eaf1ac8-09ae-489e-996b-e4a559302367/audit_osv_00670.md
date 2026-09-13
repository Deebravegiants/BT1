# [M] ALPINE-CVE-2017-5667

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2017-5667
Ecosystem: Alpine:v3.10, Alpine:v3.5, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 6.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:N/I:N/A:H)
Published: 2017-03-16
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-5667
Type: osv

## Affected
- Alpine:v3.10: `qemu` — affected >=0 <2.8.1-r1
- Alpine:v3.5: `qemu` — affected >=0 <2.8.1.1-r0
- Alpine:v3.6: `qemu` — affected >=0 <2.8.1-r1
- Alpine:v3.7: `qemu` — affected >=0 <2.8.1-r1
- Alpine:v3.8: `qemu` — affected >=0 <2.8.1-r1
- Alpine:v3.9: `qemu` — affected >=0 <2.8.1-r1

## Details
The sdhci_sdma_transfer_multi_blocks function in hw/sd/sdhci.c in QEMU (aka Quick Emulator) allows local guest OS privileged users to cause a denial of service (out-of-bounds heap access and crash) or execute arbitrary code on the QEMU host via vectors involving the data transfer length.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-5667
