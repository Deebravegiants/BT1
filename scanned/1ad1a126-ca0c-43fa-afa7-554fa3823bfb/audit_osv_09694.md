# [M] CVE-2017-10789

## Summary
Severity: Medium
Advisory: CVE-2017-10789
CVSS: 5.9 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2017-07-01
Source: https://osv.dev/vulnerability/CVE-2017-10789
Type: osv

## Details
The DBD::mysql module through 4.043 for Perl uses the mysql_ssl=1 setting to mean that SSL is optional (even though this setting's documentation has a "your communication with the server will be encrypted" statement), which allows man-in-the-middle attackers to spoof servers via a cleartext-downgrade attack, a related issue to CVE-2015-3152.

## References
- http://www.securityfocus.com/bid/99364
- https://github.com/perl5-dbi/DBD-mysql/issues/110
- https://github.com/perl5-dbi/DBD-mysql/pull/114
- https://github.com/perl5-dbi/DBD-mysql/issues/140
