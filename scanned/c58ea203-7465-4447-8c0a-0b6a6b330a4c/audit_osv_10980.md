# [C] CVE-2017-5522

## Summary
Severity: Critical
Advisory: CVE-2017-5522
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-03-15
Source: https://osv.dev/vulnerability/CVE-2017-5522
Type: osv

## Details
Stack-based buffer overflow in MapServer before 6.0.6, 6.2.x before 6.2.4, 6.4.x before 6.4.5, and 7.0.x before 7.0.4 allows remote attackers to cause a denial of service (crash) or execute arbitrary code via vectors involving WFS get feature requests.

## References
- http://www.debian.org/security/2017/dsa-3766
- http://www.mapserver.org/development/changelog/changelog-6-0-6.html#changelog-6-0-6
- http://www.mapserver.org/development/changelog/changelog-6-2-4.html#changelog-6-2-4
- http://www.mapserver.org/development/changelog/changelog-6-4.html#changelog-6-4-5
- http://www.mapserver.org/development/changelog/changelog-7-0.html#changelog-7-0-4
- https://lists.osgeo.org/pipermail/mapserver-dev/2017-January/015007.html
- https://github.com/mapserver/mapserver/commit/e52a436c0e1c5e9f7ef13428dba83194a800f4df
