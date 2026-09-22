# [M] CVE-2018-10839

## Summary
Severity: Medium
Advisory: CVE-2018-10839
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-10-16
Source: https://osv.dev/vulnerability/CVE-2018-10839
Type: osv

## Details
Qemu emulator <= 3.0.0 built with the NE2000 NIC emulation support is vulnerable to an integer overflow, which could lead to buffer overflow issue. It could occur when receiving packets over the network. A user inside guest could use this flaw to crash the Qemu process resulting in DoS.

## References
- https://access.redhat.com/errata/RHSA-2019:2892
- https://lists.debian.org/debian-lts-announce/2018/11/msg00038.html
- https://www.debian.org/security/2018/dsa-4338
- https://www.openwall.com/lists/oss-security/2018/10/08/1
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2018-10839
- https://usn.ubuntu.com/3826-1/
- https://lists.gnu.org/archive/html/qemu-devel/2018-09/msg03273.html
