# [M] CVE-2019-9074

## Summary
Severity: Medium
Advisory: CVE-2019-9074
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2019-02-24
Source: https://osv.dev/vulnerability/CVE-2019-9074
Type: osv

## Details
An issue was discovered in the Binary File Descriptor (BFD) library (aka libbfd), as distributed in GNU Binutils 2.32. It is an out-of-bounds read leading to a SEGV in bfd_getl32 in libbfd.c, when called from pex64_get_runtime_function in pei-x86_64.c.

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-10/msg00078.html
- http://lists.opensuse.org/opensuse-security-announce/2020-11/msg00004.html
- https://security.gentoo.org/glsa/202107-24
- https://support.f5.com/csp/article/K09092524
- https://usn.ubuntu.com/4336-1/
- https://sourceware.org/bugzilla/show_bug.cgi?id=24235
- https://security.netapp.com/advisory/ntap-20190314-0003/
