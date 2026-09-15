# [H] CVE-2016-1251

## Summary
Severity: High
Advisory: CVE-2016-1251
CVSS: 8.1 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2016-11-29
Source: https://osv.dev/vulnerability/CVE-2016-1251
Type: osv

## Details
There is a vulnerability of type use-after-free affecting DBD::mysql (aka DBD-mysql or the Database Interface (DBI) MySQL driver for Perl) 3.x and 4.x before 4.041 when used with mysql_server_prepare=1.

## References
- http://www.openwall.com/lists/oss-security/2016/11/28/2
- http://www.securityfocus.com/bid/94573
- https://security.gentoo.org/glsa/201701-51
- https://tracker.debian.org/news/819888
- https://anonscm.debian.org/cgit/pkg-perl/packages/libdbd-mysql-perl.git/commit/?id=a8b97e4713391b1f8beffbfddac483c276feaff1
- https://github.com/perl5-dbi/DBD-mysql/commit/3619c170461a3107a258d1fd2d00ed4832adb1b1
