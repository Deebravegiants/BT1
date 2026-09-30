# [M] CVE-2021-3507

## Summary
Severity: Medium
Advisory: CVE-2021-3507
CVSS: 6.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:L)
Published: 2021-05-06
Source: https://osv.dev/vulnerability/CVE-2021-3507
Type: osv

## Details
A heap buffer overflow was found in the floppy disk emulator of QEMU up to 6.0.0 (including). It could occur in fdctrl_transfer_handler() in hw/block/fdc.c while processing DMA read data transfers from the floppy drive to the guest system. A privileged guest user could use this flaw to crash the QEMU process on the host resulting in DoS scenario, or potential information leakage from the host memory.

## References
- https://lists.debian.org/debian-lts-announce/2022/09/msg00008.html
- https://security.netapp.com/advisory/ntap-20210528-0005/
- https://bugzilla.redhat.com/show_bug.cgi?id=1951118
