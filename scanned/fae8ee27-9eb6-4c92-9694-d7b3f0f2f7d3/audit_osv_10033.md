# [H] CVE-2017-12837

## Summary
Severity: High
Advisory: CVE-2017-12837
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-09-19
Source: https://osv.dev/vulnerability/CVE-2017-12837
Type: osv

## Details
Heap-based buffer overflow in the S_regatom function in regcomp.c in Perl 5 before 5.24.3-RC1 and 5.26.x before 5.26.1-RC1 allows remote attackers to cause a denial of service (out-of-bounds write) via a regular expression with a '\N{}' escape and the case-insensitive modifier.

## References
- https://rt.perl.org/Public/Bug/Display.html?id=131582
- https://www.oracle.com/security-alerts/cpujul2020.html
- http://www.debian.org/security/2017/dsa-3982
- http://www.securityfocus.com/bid/100860
- https://perl5.git.perl.org/perl.git/log/refs/tags/v5.24.3-RC1
- https://perl5.git.perl.org/perl.git/log/refs/tags/v5.26.1-RC1
- https://security.netapp.com/advisory/ntap-20180426-0001/
- https://bugzilla.redhat.com/show_bug.cgi?id=1492091
- https://perl5.git.perl.org/perl.git/commitdiff/96c83ed78aeea1a0496dd2b2d935869a822dc8a5
