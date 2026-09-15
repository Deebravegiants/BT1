# [H] mod_proxy_http NULL pointer dereference

## Summary
Severity: High
Advisory: BIT-apache-2020-13950
Aliases: CVE-2020-13950
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-apache-2020-13950
Type: osv

## Affected
- Bitnami: `apache` — affected >=2.4.41 <2.4.47

## Details
Apache HTTP Server versions 2.4.41 to 2.4.46 mod_proxy_http can be made to crash (NULL pointer dereference) with specially crafted requests using both Content-Length and Transfer-Encoding headers, leading to a Denial of Service

## References
- http://httpd.apache.org/security/vulnerabilities_24.html
- http://www.openwall.com/lists/oss-security/2021/06/10/4
- https://lists.apache.org/thread.html/r7f2b70b621651548f4b6f027552f1dd91705d7111bb5d15cda0a68dd%40%3Cdev.httpd.apache.org%3E
- https://lists.apache.org/thread.html/rbe197409ae4a58b629fb792d1aed541ccbbf865121a80e1c5938d223%40%3Cannounce.httpd.apache.org%3E
- https://lists.apache.org/thread.html/re026d3da9d7824bd93b9f871c0fdda978d960c7e62d8c43cba8d0bf3%40%3Ccvs.httpd.apache.org%3E
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/SPBR6WUYBJNACHKE65SPL7TJOHX7RHWD/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/ZNCYSR3BXT36FFF4XTCPL3HDQK4VP45R/
- https://security.gentoo.org/glsa/202107-38
- https://security.netapp.com/advisory/ntap-20210702-0001/
- https://www.oracle.com/security-alerts/cpuoct2021.html
- https://nvd.nist.gov/vuln/detail/CVE-2020-13950
