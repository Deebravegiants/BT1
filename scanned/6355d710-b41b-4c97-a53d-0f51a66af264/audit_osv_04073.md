# [C] HTTP request smuggling vulnerability in Apache HTTP Server 2.4.52 and earlier

## Summary
Severity: Critical
Advisory: BIT-apache-2022-22720
Aliases: CVE-2022-22720
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-apache-2022-22720
Type: osv

## Affected
- Bitnami: `apache` — affected >=0 <2.4.53

## Details
Apache HTTP Server 2.4.52 and earlier fails to close inbound connection when errors are encountered discarding the request body, exposing the server to HTTP Request Smuggling

## References
- http://seclists.org/fulldisclosure/2022/May/33
- http://seclists.org/fulldisclosure/2022/May/35
- http://seclists.org/fulldisclosure/2022/May/38
- http://www.openwall.com/lists/oss-security/2022/03/14/3
- https://httpd.apache.org/security/vulnerabilities_24.html
- https://lists.debian.org/debian-lts-announce/2022/03/msg00033.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/RGWILBORT67SHMSLYSQZG2NMXGCMPUZO/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/X73C35MMMZGBVPQQCH7LQZUMYZNQA5FO/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/Z7H26WJ6TPKNWV3QKY4BHKUKQVUTZJTD/
- https://security.gentoo.org/glsa/202208-20
- https://security.netapp.com/advisory/ntap-20220321-0001/
- https://support.apple.com/kb/HT213255
- https://support.apple.com/kb/HT213256
- https://support.apple.com/kb/HT213257
- https://www.oracle.com/security-alerts/cpuapr2022.html
- https://www.oracle.com/security-alerts/cpujul2022.html
- https://nvd.nist.gov/vuln/detail/CVE-2022-22720
