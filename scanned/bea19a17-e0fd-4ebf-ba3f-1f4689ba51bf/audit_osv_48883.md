# [M] CVE-2018-16885

## Summary
Severity: Medium
Advisory: CVE-2018-16885
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-01-03
Source: https://osv.dev/vulnerability/CVE-2018-16885
Type: osv

## Details
A flaw was found in the Linux kernel that allows the userspace to call memcpy_fromiovecend() and similar functions with a zero offset and buffer length which causes the read beyond the buffer boundaries, in certain cases causing a memory access fault and a system halt by accessing invalid memory address. This issue only affects kernel version 3.10.x as shipped with Red Hat Enterprise Linux 7.

## References
- http://www.securityfocus.com/bid/106296
- https://access.redhat.com/errata/RHSA-2019:2029
- https://access.redhat.com/errata/RHSA-2019:2043
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2018-16885
