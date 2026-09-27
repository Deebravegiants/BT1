# [C] CVE-2017-12883

## Summary
Severity: Critical
Advisory: CVE-2017-12883
CVSS: 9.1 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2017-09-19
Source: https://osv.dev/vulnerability/CVE-2017-12883
Type: osv

## Details
Buffer overflow in the S_grok_bslash_N function in regcomp.c in Perl 5 before 5.24.3-RC1 and 5.26.x before 5.26.1-RC1 allows remote attackers to disclose sensitive information or cause a denial of service (application crash) via a crafted regular expression with an invalid '\N{U+...}' escape.

## References
- https://rt.perl.org/Public/Bug/Display.html?id=131598
- https://www.oracle.com/security-alerts/cpujul2020.html
- http://www.debian.org/security/2017/dsa-3982
- http://www.securityfocus.com/bid/100852
- https://perl5.git.perl.org/perl.git/log/refs/tags/v5.24.3-RC1
- https://perl5.git.perl.org/perl.git/log/refs/tags/v5.26.1-RC1
- https://security.netapp.com/advisory/ntap-20180426-0001/
- http://mirror.cucumberlinux.com/cucumber/cucumber-1.0/source/lang-base/perl/patches/CVE-2017-12883.patch
- https://bugzilla.redhat.com/show_bug.cgi?id=1492093
- https://perl5.git.perl.org/perl.git/commitdiff/2be4edede4ae226e2eebd4eff28cedd2041f300f#patch1
