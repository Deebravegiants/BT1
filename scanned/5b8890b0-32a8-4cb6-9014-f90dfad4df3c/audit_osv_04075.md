# [C] mod_sed: Read/write beyond bounds

## Summary
Severity: Critical
Advisory: BIT-apache-2022-23943
Aliases: CVE-2022-23943
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-apache-2022-23943
Type: osv

## Affected
- Bitnami: `apache` — affected >=0 <2.4.53

## Details
Out-of-bounds Write vulnerability in mod_sed of Apache HTTP Server allows an attacker to overwrite heap memory with possibly attacker provided data. This issue affects Apache HTTP Server 2.4 version 2.4.52 and prior versions.

## References
- http://www.openwall.com/lists/oss-security/2022/03/14/1
- https://httpd.apache.org/security/vulnerabilities_24.html
- https://lists.debian.org/debian-lts-announce/2022/03/msg00033.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/RGWILBORT67SHMSLYSQZG2NMXGCMPUZO/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/X73C35MMMZGBVPQQCH7LQZUMYZNQA5FO/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/Z7H26WJ6TPKNWV3QKY4BHKUKQVUTZJTD/
- https://security.gentoo.org/glsa/202208-20
- https://security.netapp.com/advisory/ntap-20220321-0001/
- https://www.oracle.com/security-alerts/cpuapr2022.html
- https://www.tenable.com/security/tns-2022-08
- https://www.tenable.com/security/tns-2022-09
- https://nvd.nist.gov/vuln/detail/CVE-2022-23943
