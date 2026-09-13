# [M] CVE-2018-18701

## Summary
Severity: Medium
Advisory: CVE-2018-18701
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-10-29
Source: https://osv.dev/vulnerability/CVE-2018-18701
Type: osv

## Details
An issue was discovered in cp-demangle.c in GNU libiberty, as distributed in GNU Binutils 2.31. There is a stack consumption vulnerability resulting from infinite recursion in the functions next_is_type_qual() and cplus_demangle_type() in cp-demangle.c. Remote attackers could leverage this vulnerability to cause a denial-of-service via an ELF file, as demonstrated by nm.

## References
- https://usn.ubuntu.com/4326-1/
- https://usn.ubuntu.com/4336-1/
- https://gcc.gnu.org/bugzilla/show_bug.cgi?id=87675
