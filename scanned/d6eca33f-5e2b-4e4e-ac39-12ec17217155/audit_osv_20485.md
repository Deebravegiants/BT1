# [M] CVE-2021-3416

## Summary
Severity: Medium
Advisory: CVE-2021-3416
CVSS: 6.0 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:C/C:N/I:N/A:H)
Published: 2021-03-18
Source: https://osv.dev/vulnerability/CVE-2021-3416
Type: osv

## Details
A potential stack overflow via infinite loop issue was found in various NIC emulators of QEMU in versions up to and including 5.2.0. The issue occurs in loopback mode of a NIC wherein reentrant DMA checks get bypassed. A guest user/process may use this flaw to consume CPU cycles or crash the QEMU process on the host resulting in DoS scenario.

## References
- https://lists.debian.org/debian-lts-announce/2021/04/msg00009.html
- https://lists.debian.org/debian-lts-announce/2022/09/msg00008.html
- https://security.gentoo.org/glsa/202208-27
- https://security.netapp.com/advisory/ntap-20210507-0002/
- https://bugzilla.redhat.com/show_bug.cgi?id=1932827
- https://www.openwall.com/lists/oss-security/2021/02/26/1
