# [C] CVE-2017-15804

## Summary
Severity: Critical
Advisory: CVE-2017-15804
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-10-22
Source: https://osv.dev/vulnerability/CVE-2017-15804
Type: osv

## Details
The glob function in glob.c in the GNU C Library (aka glibc or libc6) before 2.27 contains a buffer overflow during unescaping of user names with the ~ operator.

## References
- http://www.securityfocus.com/bid/101535
- https://sourceware.org/git/gitweb.cgi?p=glibc.git%3Ba=commit%3Bh=a159b53fa059947cc2548e3b0d5bdcf7b9630ba8
- https://access.redhat.com/errata/RHSA-2018:0805
- https://access.redhat.com/errata/RHSA-2018:1879
- https://sourceware.org/bugzilla/show_bug.cgi?id=22332
