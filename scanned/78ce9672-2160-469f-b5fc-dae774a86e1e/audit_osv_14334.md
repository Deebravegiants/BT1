# [M] CVE-2018-9138

## Summary
Severity: Medium
Advisory: CVE-2018-9138
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-03-30
Source: https://osv.dev/vulnerability/CVE-2018-9138
Type: osv

## Details
An issue was discovered in cplus-dem.c in GNU libiberty, as distributed in GNU Binutils 2.29 and 2.30. Stack Exhaustion occurs in the C++ demangling functions provided by libiberty, and there are recursive stack frames: demangle_nested_args, demangle_args, do_arg, and do_type.

## References
- https://usn.ubuntu.com/4326-1/
- https://usn.ubuntu.com/4336-1/
- https://sourceware.org/bugzilla/show_bug.cgi?id=23008
