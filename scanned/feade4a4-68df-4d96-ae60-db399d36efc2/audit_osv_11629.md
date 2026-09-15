# [C] CVE-2017-9119

## Summary
Severity: Critical
Advisory: CVE-2017-9119
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-05-21
Source: https://osv.dev/vulnerability/CVE-2017-9119
Type: osv

## Details
The i_zval_ptr_dtor function in Zend/zend_variables.h in PHP 7.1.5 allows attackers to cause a denial of service (memory consumption and application crash) or possibly have unspecified other impact by triggering crafted operations on array data structures.

## References
- http://www.securityfocus.com/bid/98596
- https://security.netapp.com/advisory/ntap-20180112-0001/
- https://bugs.php.net/bug.php?id=74593
