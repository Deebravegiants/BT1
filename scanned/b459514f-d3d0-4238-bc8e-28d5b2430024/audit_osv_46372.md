# [M] CVE-2006-7254

## Summary
Severity: Medium
Advisory: CVE-2006-7254
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-04-10
Source: https://osv.dev/vulnerability/CVE-2006-7254
Type: osv

## Details
The nscd daemon in the GNU C Library (glibc) before version 2.5 does not close incoming client sockets if they cannot be handled by the daemon, allowing local users to carry out a denial of service attack on the daemon.

## References
- https://sourceware.org/bugzilla/show_bug.cgi?id=2498
- https://sourceware.org/bugzilla/show_bug.cgi?id=2498
- https://sourceware.org/bugzilla/show_bug.cgi?id=2498
