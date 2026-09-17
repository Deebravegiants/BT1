# [C] CVE-2017-8923

## Summary
Severity: Critical
Advisory: CVE-2017-8923
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-05-12
Source: https://osv.dev/vulnerability/CVE-2017-8923
Type: osv

## Details
The zend_string_extend function in Zend/zend_string.h in PHP through 7.1.5 does not prevent changes to string objects that result in a negative length, which allows remote attackers to cause a denial of service (application crash) or possibly have unspecified other impact by leveraging a script's use of .= with a long string.

## References
- http://www.securityfocus.com/bid/98518
- https://security.netapp.com/advisory/ntap-20241227-0007/
- https://bugs.php.net/bug.php?id=74577
