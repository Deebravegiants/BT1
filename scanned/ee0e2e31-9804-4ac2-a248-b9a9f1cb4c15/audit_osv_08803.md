# [M] CVE-2016-6190

## Summary
Severity: Medium
Advisory: CVE-2016-6190
CVSS: 4.3 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2017-02-17
Source: https://osv.dev/vulnerability/CVE-2016-6190
Type: osv

## Details
SOGo before 2.3.12 and 3.x before 3.1.1 does not restrict access to the UID and DTSTAMP attributes, which allows remote authenticated users to obtain sensitive information about appointments with the "View the Date & Time" restriction, as demonstrated by correlating UIDs and DTSTAMPs between all users.

## References
- http://www.openwall.com/lists/oss-security/2016/07/09/3
- https://sogo.nu/bugs/view.php?id=3696
- https://github.com/inverse-inc/sogo/commit/717f45f640a2866b76a8984139391fae64339225
- https://github.com/inverse-inc/sogo/commit/875a4aca3218340fd4d3141950c82c2ff45b343d
