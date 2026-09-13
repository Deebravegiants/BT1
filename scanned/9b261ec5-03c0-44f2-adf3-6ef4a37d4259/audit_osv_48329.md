# [H] CVE-2017-6949

## Summary
Severity: High
Advisory: CVE-2017-6949
CVSS: 8.1 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-03-16
Source: https://osv.dev/vulnerability/CVE-2017-6949
Type: osv

## Details
An issue was discovered in CHICKEN Scheme through 4.12.0. When using a nonstandard CHICKEN-specific extension to allocate an SRFI-4 vector in unmanaged memory, the vector size would be used in unsanitised form as an argument to malloc(). With an unexpected size, the impact may have been a segfault or buffer overflow.

## References
- http://www.securityfocus.com/bid/97317
- http://lists.gnu.org/archive/html/chicken-announce/2017-03/msg00000.html
