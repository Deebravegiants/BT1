# [M] CVE-2020-10690

## Summary
Severity: Medium
Advisory: CVE-2020-10690
CVSS: 6.4 (CVSS:3.1/AV:L/AC:H/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-05-08
Source: https://osv.dev/vulnerability/CVE-2020-10690
Type: osv

## Details
There is a use-after-free in kernel versions before 5.5 due to a race condition between the release of ptp_clock and cdev while resource deallocation. When a (high privileged) process allocates a ptp device file (like /dev/ptpX) and voluntarily goes to sleep. During this time if the underlying device is removed, it can cause an exploitable condition as the process wakes up to terminate and clean all attached files. The system crashes due to the cdev structure being invalid (as already freed) which is pointed to by the inode.

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-06/msg00022.html
- https://lists.debian.org/debian-lts-announce/2020/06/msg00011.html
- https://lists.debian.org/debian-lts-announce/2020/06/msg00013.html
- https://security.netapp.com/advisory/ntap-20200608-0001/
- https://usn.ubuntu.com/4419-1/
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2020-10690
