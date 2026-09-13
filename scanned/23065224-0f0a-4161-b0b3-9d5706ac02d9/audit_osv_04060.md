# [H] mod_auth_digest possible stack overflow by one nul byte

## Summary
Severity: High
Advisory: BIT-apache-2020-35452
Aliases: CVE-2020-35452
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-apache-2020-35452
Type: osv

## Affected
- Bitnami: `apache` — affected >=2.4.0 <2.4.47

## Details
Apache HTTP Server versions 2.4.0 to 2.4.46 A specially crafted Digest nonce can cause a stack overflow in mod_auth_digest. There is no report of this overflow being exploitable, nor the Apache HTTP Server team could create one, though some particular compiler and/or compilation option might make it possible, with limited consequences anyway due to the size (a single byte) and the value (zero byte) of the overflow

## References
- http://httpd.apache.org/security/vulnerabilities_24.html
- http://www.openwall.com/lists/oss-security/2021/06/10/5
- https://lists.apache.org/thread.html/r7f2b70b621651548f4b6f027552f1dd91705d7111bb5d15cda0a68dd%40%3Cdev.httpd.apache.org%3E
- https://lists.apache.org/thread.html/rccb1b8225583a48c6360edc7a93cc97ae8b0215791e455dc607e7602%40%3Cannounce.httpd.apache.org%3E
- https://lists.apache.org/thread.html/re026d3da9d7824bd93b9f871c0fdda978d960c7e62d8c43cba8d0bf3%40%3Ccvs.httpd.apache.org%3E
- https://lists.debian.org/debian-lts-announce/2021/07/msg00006.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/SPBR6WUYBJNACHKE65SPL7TJOHX7RHWD/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/ZNCYSR3BXT36FFF4XTCPL3HDQK4VP45R/
- https://security.gentoo.org/glsa/202107-38
- https://security.netapp.com/advisory/ntap-20210702-0001/
- https://www.debian.org/security/2021/dsa-4937
- https://www.oracle.com/security-alerts/cpuoct2021.html
- https://nvd.nist.gov/vuln/detail/CVE-2020-35452
