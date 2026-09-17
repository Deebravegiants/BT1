# [M] CVE-2016-10739

## Summary
Severity: Medium
Advisory: CVE-2016-10739
CVSS: 5.3 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L)
Published: 2019-01-21
Source: https://osv.dev/vulnerability/CVE-2016-10739
Type: osv

## Details
In the GNU C Library (aka glibc or libc6) through 2.28, the getaddrinfo function would successfully parse a string that contained an IPv4 address followed by whitespace and arbitrary characters, which could lead applications to incorrectly assume that it had parsed a valid string, without the possibility of embedded HTTP headers or other potentially dangerous substrings.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-04/msg00082.html
- http://www.securityfocus.com/bid/106672
- https://access.redhat.com/errata/RHSA-2019:2118
- https://access.redhat.com/errata/RHSA-2019:3513
- https://bugzilla.redhat.com/show_bug.cgi?id=1347549
- https://sourceware.org/bugzilla/show_bug.cgi?id=20018
