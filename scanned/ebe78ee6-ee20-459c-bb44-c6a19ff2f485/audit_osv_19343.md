# [M] CVE-2021-20255

## Summary
Severity: Medium
Advisory: CVE-2021-20255
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-03-09
Source: https://osv.dev/vulnerability/CVE-2021-20255
Type: osv

## Details
A stack overflow via an infinite recursion vulnerability was found in the eepro100 i8255x device emulator of QEMU. This issue occurs while processing controller commands due to a DMA reentry issue. This flaw allows a guest user or process to consume CPU cycles or crash the QEMU process on the host, resulting in a denial of service. The highest threat from this vulnerability is to system availability.

## References
- https://lists.debian.org/debian-lts-announce/2021/04/msg00009.html
- https://ruhr-uni-bochum.sciebo.de/s/NNWP2GfwzYKeKwE?path=%2Feepro100_stackoverflow1
- https://security.netapp.com/advisory/ntap-20210507-0003/
- https://bugzilla.redhat.com/show_bug.cgi?id=1930646
- https://www.openwall.com/lists/oss-security/2021/02/25/1
