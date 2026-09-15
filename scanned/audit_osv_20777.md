# [H] CVE-2021-3682

## Summary
Severity: High
Advisory: CVE-2021-3682
CVSS: 8.5 (CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2021-08-05
Source: https://osv.dev/vulnerability/CVE-2021-3682
Type: osv

## Details
A flaw was found in the USB redirector device emulation of QEMU in versions prior to 6.1.0-rc2. It occurs when dropping packets during a bulk transfer from a SPICE client due to the packet queue being full. A malicious SPICE client could use this flaw to make QEMU call free() with faked heap chunk metadata, resulting in a crash of QEMU or potential code execution with the privileges of the QEMU process on the host.

## References
- https://lists.debian.org/debian-lts-announce/2021/09/msg00000.html
- https://lists.debian.org/debian-lts-announce/2022/09/msg00008.html
- https://security.gentoo.org/glsa/202208-27
- https://security.netapp.com/advisory/ntap-20210902-0006/
- https://www.debian.org/security/2021/dsa-4980
- https://bugzilla.redhat.com/show_bug.cgi?id=1989651
