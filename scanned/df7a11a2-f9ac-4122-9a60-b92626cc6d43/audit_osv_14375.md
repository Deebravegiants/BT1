# [M] CVE-2018-9996

## Summary
Severity: Medium
Advisory: CVE-2018-9996
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-04-10
Source: https://osv.dev/vulnerability/CVE-2018-9996
Type: osv

## Details
An issue was discovered in cplus-dem.c in GNU libiberty, as distributed in GNU Binutils 2.30. Stack Exhaustion occurs in the C++ demangling functions provided by libiberty, and there are recursive stack frames: demangle_template_value_parm, demangle_integral_value, and demangle_expression.

## References
- http://www.securityfocus.com/bid/103733
- https://gcc.gnu.org/bugzilla/show_bug.cgi?id=85304
