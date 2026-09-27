# [M] CVE-2015-8777

## Summary
Severity: Medium
Advisory: CVE-2015-8777
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N)
Published: 2016-01-20
Source: https://osv.dev/vulnerability/CVE-2015-8777
Type: osv

## Details
The process_envvars function in elf/rtld.c in the GNU C Library (aka glibc or libc6) before 2.23 allows local users to bypass a pointer-guarding protection mechanism via a zero value of the LD_POINTER_GUARD environment variable.

## References
- http://www.debian.org/security/2016/dsa-3480
- http://www.ubuntu.com/usn/USN-2985-1
- http://www.ubuntu.com/usn/USN-2985-2
- https://access.redhat.com/errata/RHSA-2017:1916
- https://security.gentoo.org/glsa/201702-11
- http://hmarco.org/bugs/glibc_ptr_mangle_weakness.html
- https://sourceware.org/bugzilla/show_bug.cgi?id=18928
- http://lists.fedoraproject.org/pipermail/package-announce/2016-February/177404.html
- http://lists.opensuse.org/opensuse-security-announce/2016-02/msg00036.html
- http://lists.opensuse.org/opensuse-security-announce/2016-02/msg00037.html
- http://lists.opensuse.org/opensuse-security-announce/2016-02/msg00038.html
- http://lists.opensuse.org/opensuse-security-announce/2016-02/msg00039.html
- http://www.openwall.com/lists/oss-security/2016/01/20/1
- http://www.securityfocus.com/bid/81469
- http://www.securitytracker.com/id/1034811
