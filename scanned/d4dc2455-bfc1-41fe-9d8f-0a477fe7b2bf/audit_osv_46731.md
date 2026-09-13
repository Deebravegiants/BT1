# [C] CVE-2014-9906

## Summary
Severity: Critical
Advisory: CVE-2014-9906
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2016-08-19
Source: https://osv.dev/vulnerability/CVE-2014-9906
Type: osv

## Details
Use-after-free vulnerability in DBD::mysql before 4.029 allows attackers to cause a denial of service (program crash) or possibly execute arbitrary code via vectors related to a lost server connection.

## References
- http://cpansearch.perl.org/src/CAPTTOFU/DBD-mysql-4.029/ChangeLog
- http://www.debian.org/security/2016/dsa-3635
- http://www.openwall.com/lists/oss-security/2016/07/27/5
- http://www.openwall.com/lists/oss-security/2016/07/27/6
- http://www.openwall.com/lists/oss-security/2016/07/27/5
- http://www.openwall.com/lists/oss-security/2016/07/27/6
- https://github.com/perl5-dbi/DBD-mysql/commit/a56ae87a4c1c1fead7d09c3653905841ccccf1cc
- https://github.com/perl5-dbi/DBD-mysql/commit/a56ae87a4c1c1fead7d09c3653905841ccccf1cc
- https://rt.cpan.org/Public/Bug/Display.html?id=97625
- http://www.securityfocus.com/bid/92149
