# [M] CVE-2019-7309

## Summary
Severity: Medium
Advisory: CVE-2019-7309
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-02-03
Source: https://osv.dev/vulnerability/CVE-2019-7309
Type: osv

## Details
In the GNU C Library (aka glibc or libc6) through 2.29, the memcmp function for the x32 architecture can incorrectly return zero (indicating that the inputs are equal) because the RDX most significant bit is mishandled.

## References
- http://www.securityfocus.com/bid/106835
- https://security.gentoo.org/glsa/202006-04
- https://sourceware.org/ml/libc-alpha/2019-02/msg00041.html
- https://sourceware.org/bugzilla/show_bug.cgi?id=24155
