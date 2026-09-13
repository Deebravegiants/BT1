# [M] CVE-2018-17794

## Summary
Severity: Medium
Advisory: CVE-2018-17794
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-09-30
Source: https://osv.dev/vulnerability/CVE-2018-17794
Type: osv

## Details
An issue was discovered in cplus-dem.c in GNU libiberty, as distributed in GNU Binutils 2.31. There is a NULL pointer dereference in work_stuff_copy_to_from when called from iterate_demangle_function.

## References
- https://usn.ubuntu.com/4326-1/
- https://usn.ubuntu.com/4336-1/
- https://gcc.gnu.org/bugzilla/show_bug.cgi?id=87350
