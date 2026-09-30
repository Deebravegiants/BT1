# [H] CVE-2021-3530

## Summary
Severity: High
Advisory: CVE-2021-3530
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-06-02
Source: https://osv.dev/vulnerability/CVE-2021-3530
Type: osv

## Details
A flaw was discovered in GNU libiberty within demangle_path() in rust-demangle.c, as distributed in GNU Binutils version 2.36. A crafted symbol can cause stack memory to be exhausted leading to a crash.

## References
- https://security.gentoo.org/glsa/202208-30
- https://security.netapp.com/advisory/ntap-20210716-0006/
- https://bugzilla.redhat.com/show_bug.cgi?id=1956423
- https://src.fedoraproject.org/rpms/binutils/blob/rawhide/f/binutils-CVE-2021-3530.patch
