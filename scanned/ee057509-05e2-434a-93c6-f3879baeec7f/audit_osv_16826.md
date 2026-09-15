# [C] CVE-2019-9893

## Summary
Severity: Critical
Advisory: CVE-2019-9893
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-03-21
Source: https://osv.dev/vulnerability/CVE-2019-9893
Type: osv

## Details
libseccomp before 2.4.0 did not correctly generate 64-bit syscall argument comparisons using the arithmetic operators (LT, GT, LE, GE), which might able to lead to bypassing seccomp filters and potential privilege escalations.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-10/msg00022.html
- http://lists.opensuse.org/opensuse-security-announce/2019-10/msg00027.html
- https://usn.ubuntu.com/4001-1/
- https://usn.ubuntu.com/4001-2/
- https://access.redhat.com/errata/RHSA-2019:3624
- https://security.gentoo.org/glsa/201904-18
- https://github.com/seccomp/libseccomp/issues/139
- https://seclists.org/oss-sec/2019/q1/179
