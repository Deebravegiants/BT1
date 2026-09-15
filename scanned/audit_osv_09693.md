# [C] CVE-2017-10788

## Summary
Severity: Critical
Advisory: CVE-2017-10788
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-07-01
Source: https://osv.dev/vulnerability/CVE-2017-10788
Type: osv

## Details
The DBD::mysql module through 4.043 for Perl allows remote attackers to cause a denial of service (use-after-free and application crash) or possibly have unspecified other impact by triggering (1) certain error responses from a MySQL server or (2) a loss of a network connection to a MySQL server. The use-after-free defect was introduced by relying on incorrect Oracle mysql_stmt_close documentation and code examples.

## References
- http://seclists.org/oss-sec/2017/q2/443
- http://www.securityfocus.com/bid/99374
- https://github.com/perl5-dbi/DBD-mysql/issues/120
