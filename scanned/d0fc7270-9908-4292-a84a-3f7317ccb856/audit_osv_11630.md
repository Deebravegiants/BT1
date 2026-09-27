# [C] CVE-2017-9120

## Summary
Severity: Critical
Advisory: CVE-2017-9120
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-08-02
Source: https://osv.dev/vulnerability/CVE-2017-9120
Type: osv

## Details
PHP 7.x through 7.1.5 allows remote attackers to cause a denial of service (buffer overflow and application crash) or possibly have unspecified other impact via a long string because of an Integer overflow in mysqli_real_escape_string.

## References
- https://access.redhat.com/errata/RHSA-2019:2519
- https://security.netapp.com/advisory/ntap-20181107-0003/
- https://bugs.php.net/bug.php?id=74544
