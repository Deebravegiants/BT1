# [H] CVE-2016-1246

## Summary
Severity: High
Advisory: CVE-2016-1246
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-10-05
Source: https://osv.dev/vulnerability/CVE-2016-1246
Type: osv

## Details
Buffer overflow in the DBD::mysql module before 4.037 for Perl allows context-dependent attackers to cause a denial of service (crash) via vectors related to an error message.

## References
- http://blogs.perl.org/users/mike_b/2016/10/security-release---buffer-overflow-in-dbdmysql-perl-library.html
- http://www.debian.org/security/2016/dsa-3684
- http://www.securityfocus.com/bid/93337
- https://github.com/perl5-dbi/DBD-mysql/commit/7c164a0c86cec6ee95df1d141e67b0e85dfdefd2
- https://security.gentoo.org/glsa/201701-51
