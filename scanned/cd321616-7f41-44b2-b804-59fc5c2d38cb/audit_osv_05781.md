# [M] BIT-guacamole-2020-9498

## Summary
Severity: Medium
Advisory: BIT-guacamole-2020-9498
Aliases: BIT-guacamole-server-2020-9498, CVE-2020-9498
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-guacamole-2020-9498
Type: osv

## Affected
- Bitnami: `guacamole` — affected >=0 <1.1.0

## Details
Apache Guacamole 1.1.0 and older may mishandle pointers involved inprocessing data received via RDP static virtual channels. If a userconnects to a malicious or compromised RDP server, a series ofspecially-crafted PDUs could result in memory corruption, possiblyallowing arbitrary code to be executed with the privileges of therunning guacd process.

## References
- https://kb.pulsesecure.net/articles/Pulse_Security_Advisories/SA44525
- https://lists.apache.org/thread.html/r1125f3044a0946d1e7e6f125a6170b58d413ebd4a95157e4608041c7%40%3Cannounce.apache.org%3E
- https://lists.apache.org/thread.html/r26fb170edebff842c74aacdb1333c1338f0e19e5ec7854d72e4680fc%40%3Cannounce.apache.org%3E
- https://lists.apache.org/thread.html/r90890afea72a9571d666820b2fe5942a0a5f86be406fa31da3dd0922%40%3Cannounce.apache.org%3E
- https://lists.apache.org/thread.html/rff824b38ebd2fddc726b816f0e509696b83b9f78979d0cd021ca623b%40%3Cannounce.guacamole.apache.org%3E
- https://lists.debian.org/debian-lts-announce/2020/11/msg00010.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/TVV5K2X4EXSAVUUL7IJ3MUJ3ADWMVSBM/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/WNS7UHBOFV6JHWH5XOEZTE3BREGRSSQ3/
- https://research.checkpoint.com/2020/apache-guacamole-rce/
