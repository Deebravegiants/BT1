# [H] null pointer dereference in h2 fuzzing

## Summary
Severity: High
Advisory: BIT-apache-2021-41524
Aliases: CVE-2021-41524
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-apache-2021-41524
Type: osv

## Affected
- Bitnami: `apache` — affected >=2.4.49 <2.4.50

## Details
While fuzzing the 2.4.49 httpd, a new null pointer dereference was detected during HTTP/2 request processing, allowing an external source to DoS the server. This requires a specially crafted request. The vulnerability was recently introduced in version 2.4.49. No exploit is known to the project.

## References
- http://www.openwall.com/lists/oss-security/2021/10/05/1
- https://httpd.apache.org/security/vulnerabilities_24.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/DSM6UWQICBJ2TU727RENU3HBKEAFLT6T/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/EUVJVRJRBW5QVX4OY3NOHZDQ3B3YOTSG/
- https://security.gentoo.org/glsa/202208-20
- https://security.netapp.com/advisory/ntap-20211029-0009/
- https://tools.cisco.com/security/center/content/CiscoSecurityAdvisory/cisco-sa-apache-httpd-pathtrv-LAzg68cZ
- https://www.oracle.com/security-alerts/cpujan2022.html
- https://nvd.nist.gov/vuln/detail/CVE-2021-41524
