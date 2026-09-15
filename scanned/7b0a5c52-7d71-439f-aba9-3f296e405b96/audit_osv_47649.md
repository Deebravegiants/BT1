# [M] CVE-2016-9844

## Summary
Severity: Medium
Advisory: CVE-2016-9844
CVSS: 4.0 (CVSS:3.0/AV:L/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2017-01-18
Source: https://osv.dev/vulnerability/CVE-2016-9844
Type: osv

## Details
Buffer overflow in the zi_short function in zipinfo.c in Info-Zip UnZip 6.0 allows remote attackers to cause a denial of service (crash) via a large compression method value in the central directory file header.

## References
- http://www.securityfocus.com/bid/94728
- http://www.openwall.com/lists/oss-security/2016/12/05/13
- http://www.openwall.com/lists/oss-security/2016/12/05/19
- http://www.openwall.com/lists/oss-security/2016/12/05/20
- https://bugs.launchpad.net/ubuntu/+source/unzip/+bug/1643750
