# [M] CVE-2017-12132

## Summary
Severity: Medium
Advisory: CVE-2017-12132
CVSS: 5.9 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2017-08-01
Source: https://osv.dev/vulnerability/CVE-2017-12132
Type: osv

## Details
The DNS stub resolver in the GNU C Library (aka glibc or libc6) before version 2.26, when EDNS support is enabled, will solicit large UDP responses from name servers, potentially simplifying off-path DNS spoofing attacks due to IP fragmentation.

## References
- http://www.securityfocus.com/bid/100598
- https://access.redhat.com/errata/RHSA-2018:0805
- https://arxiv.org/pdf/1205.4011.pdf
- https://sourceware.org/bugzilla/show_bug.cgi?id=21361
