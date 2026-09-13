# [M] CVE-2021-20221

## Summary
Severity: Medium
Advisory: CVE-2021-20221
CVSS: 6.0 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:C/C:N/I:N/A:H)
Published: 2021-05-13
Source: https://osv.dev/vulnerability/CVE-2021-20221
Type: osv

## Details
An out-of-bounds heap buffer access issue was found in the ARM Generic Interrupt Controller emulator of QEMU up to and including qemu 4.2.0on aarch64 platform. The issue occurs because while writing an interrupt ID to the controller memory area, it is not masked to be 4 bits wide. It may lead to the said issue while updating controller state fields and their subsequent processing. A privileged guest user may use this flaw to crash the QEMU process on the host resulting in DoS scenario.

## References
- https://lists.debian.org/debian-lts-announce/2021/02/msg00024.html
- https://lists.debian.org/debian-lts-announce/2022/09/msg00008.html
- https://security.netapp.com/advisory/ntap-20210708-0005/
- http://www.openwall.com/lists/oss-security/2021/02/05/1
- https://bugzilla.redhat.com/show_bug.cgi?id=1924601
