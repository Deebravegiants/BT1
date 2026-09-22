# [H] mod_proxy_ajp: Possible request smuggling

## Summary
Severity: High
Advisory: BIT-apache-2022-26377
Aliases: CVE-2022-26377
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-apache-2022-26377
Type: osv

## Affected
- Bitnami: `apache` — affected >=0 <2.4.54

## Details
Inconsistent Interpretation of HTTP Requests ('HTTP Request Smuggling') vulnerability in mod_proxy_ajp of Apache HTTP Server allows an attacker to smuggle requests to the AJP server it forwards requests to. This issue affects Apache HTTP Server Apache HTTP Server 2.4 version 2.4.53 and prior versions.

## References
- http://www.openwall.com/lists/oss-security/2022/06/08/2
- https://httpd.apache.org/security/vulnerabilities_24.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/7QUGG2QZWHTITMABFLVXA4DNYUOTPWYQ/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/YPY2BLEVJWFH34AX77ZJPLD2OOBYR6ND/
- https://security.gentoo.org/glsa/202208-20
- https://security.netapp.com/advisory/ntap-20220624-0005/
- https://nvd.nist.gov/vuln/detail/CVE-2022-26377
