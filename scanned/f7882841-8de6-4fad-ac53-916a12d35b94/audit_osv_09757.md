# [C] CVE-2017-11362

## Summary
Severity: Critical
Advisory: CVE-2017-11362
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-07-17
Source: https://osv.dev/vulnerability/CVE-2017-11362
Type: osv

## Details
In PHP 7.x before 7.0.21 and 7.1.x before 7.1.7, ext/intl/msgformat/msgformat_parse.c does not restrict the locale length, which allows remote attackers to cause a denial of service (stack-based buffer overflow and application crash) or possibly have unspecified other impact within International Components for Unicode (ICU) for C/C++ via a long first argument to the msgfmt_parse_message function.

## References
- https://usn.ubuntu.com/3566-2/
- https://access.redhat.com/errata/RHSA-2018:1296
- https://security.gentoo.org/glsa/201709-21
- https://security.netapp.com/advisory/ntap-20180112-0001/
- https://bugs.php.net/bug.php?id=73473
