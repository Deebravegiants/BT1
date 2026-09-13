# [M] CVE-2020-12114

## Summary
Severity: Medium
Advisory: CVE-2020-12114
CVSS: 4.7 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-05-04
Source: https://osv.dev/vulnerability/CVE-2020-12114
Type: osv

## Details
A pivot_root race condition in fs/namespace.c in the Linux kernel 4.4.x before 4.4.221, 4.9.x before 4.9.221, 4.14.x before 4.14.178, 4.19.x before 4.19.119, and 5.x before 5.3 allows local users to cause a denial of service (panic) by corrupting a mountpoint reference counter.

## References
- https://usn.ubuntu.com/4388-1/
- https://usn.ubuntu.com/4389-1/
- https://www.oracle.com/security-alerts/cpuApr2021.html
- https://usn.ubuntu.com/4391-1/
- https://usn.ubuntu.com/4392-1/
- https://usn.ubuntu.com/4390-1/
- http://lists.opensuse.org/opensuse-security-announce/2020-06/msg00022.html
- https://lists.debian.org/debian-lts-announce/2020/06/msg00011.html
- http://packetstormsecurity.com/files/159565/Kernel-Live-Patch-Security-Notice-LSN-0072-1.html
- https://lists.debian.org/debian-lts-announce/2020/06/msg00012.html
- https://lists.debian.org/debian-lts-announce/2020/06/msg00013.html
- https://usn.ubuntu.com/4387-1/
- https://www.debian.org/security/2020/dsa-4698
- https://security.netapp.com/advisory/ntap-20200608-0001/
- https://www.debian.org/security/2020/dsa-4699
- http://www.openwall.com/lists/oss-security/2020/05/04/2
