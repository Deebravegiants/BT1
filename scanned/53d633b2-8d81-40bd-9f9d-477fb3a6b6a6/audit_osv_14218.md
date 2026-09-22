# [H] CVE-2018-8019

## Summary
Severity: High
Advisory: CVE-2018-8019
CVSS: 7.4 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2018-07-31
Source: https://osv.dev/vulnerability/CVE-2018-8019
Type: osv

## Details
When using an OCSP responder Apache Tomcat Native 1.2.0 to 1.2.16 and 1.1.23 to 1.1.34 did not correctly handle invalid responses. This allowed for revoked client certificates to be incorrectly identified. It was therefore possible for users to authenticate with revoked certificates when using mutual TLS. Users not using OCSP checks are not affected by this vulnerability.

## References
- https://lists.apache.org/thread.html/ba661b0edd913b39ff129a32d855620dd861883ade05fd88a8ce517d%40%3Cdev.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/f8e0814e11c7f21f42224b6de111cb3f5e5ab5c15b78924c516d4ec2%40%3Cdev.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/re3b72cbb13e1dfe85c4a06959a3b6ca6d939b407ecca80db12b54220%40%3Cdev.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/rf8e8c091182b45daa50d3557cad9b10bb4198e3f08cf8f1c66a1b08d%40%3Cdev.tomcat.apache.org%3E
- http://mail-archives.apache.org/mod_mbox/www-announce/201807.mbox/%3C20180721095943.GA24320%40minotaur.apache.org%3E
- http://www.securityfocus.com/bid/104936
- http://www.securitytracker.com/id/1041507
- https://access.redhat.com/errata/RHSA-2018:2469
- https://access.redhat.com/errata/RHSA-2018:2470
- https://lists.debian.org/debian-lts-announce/2018/08/msg00023.html
