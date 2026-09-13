# [M] CVE-2021-4095

## Summary
Severity: Medium
Advisory: CVE-2021-4095
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-03-10
Source: https://osv.dev/vulnerability/CVE-2021-4095
Type: osv

## Details
A NULL pointer dereference was found in the Linux kernel's KVM when dirty ring logging is enabled without an active vCPU context. An unprivileged local attacker on the host may use this flaw to cause a kernel oops condition and thus a denial of service by issuing a KVM_XEN_HVM_SET_ATTR ioctl. This flaw affects Linux kernel versions prior to 5.17-rc1.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/QIOQN7JJNN6ABIDGRSTVZA65MHRLMH2Q/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/VT6573CGKVK3DU2632VVO5BVM4IU7SBV/
- http://www.openwall.com/lists/oss-security/2022/01/17/1
- https://bugzilla.redhat.com/show_bug.cgi?id=2031194
