# [C] CVE-2017-15670

## Summary
Severity: Critical
Advisory: CVE-2017-15670
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-10-20
Source: https://osv.dev/vulnerability/CVE-2017-15670
Type: osv

## Details
The GNU C Library (aka glibc or libc6) before 2.27 contains an off-by-one error leading to a heap-based buffer overflow in the glob function in glob.c, related to the processing of home directories using the ~ operator followed by a long string.

## References
- http://www.securityfocus.com/bid/101521
- https://access.redhat.com/errata/RHSA-2018:0805
- https://access.redhat.com/errata/RHSA-2018:1879
- https://sourceware.org/bugzilla/show_bug.cgi?id=22320
