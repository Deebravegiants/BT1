# [M] CVE-2020-35504

## Summary
Severity: Medium
Advisory: CVE-2020-35504
CVSS: 6.0 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:C/C:N/I:N/A:H)
Published: 2021-05-28
Source: https://osv.dev/vulnerability/CVE-2020-35504
Type: osv

## Details
A NULL pointer dereference flaw was found in the SCSI emulation support of QEMU in versions before 6.0.0. This flaw allows a privileged guest user to crash the QEMU process on the host, resulting in a denial of service. The highest threat from this vulnerability is to system availability.

## References
- https://lists.debian.org/debian-lts-announce/2022/09/msg00008.html
- https://security.gentoo.org/glsa/202208-27
- https://security.netapp.com/advisory/ntap-20210713-0006/
- http://www.openwall.com/lists/oss-security/2021/04/16/3
- https://bugzilla.redhat.com/show_bug.cgi?id=1909766
- https://www.openwall.com/lists/oss-security/2021/04/16/3
