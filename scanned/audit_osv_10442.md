# [M] CVE-2017-15671

## Summary
Severity: Medium
Advisory: CVE-2017-15671
CVSS: 5.9 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-10-20
Source: https://osv.dev/vulnerability/CVE-2017-15671
Type: osv

## Details
The glob function in glob.c in the GNU C Library (aka glibc or libc6) before 2.27, when invoked with GLOB_TILDE, could skip freeing allocated memory when processing the ~ operator with a long user name, potentially leading to a denial of service (memory leak).

## References
- http://www.securityfocus.com/bid/101517
- https://sourceware.org/bugzilla/show_bug.cgi?id=22325
