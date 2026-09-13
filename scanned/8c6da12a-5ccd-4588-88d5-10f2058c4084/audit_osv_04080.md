# [H] Denial of service in mod_lua r:parsebody

## Summary
Severity: High
Advisory: BIT-apache-2022-29404
Aliases: CVE-2022-29404
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-apache-2022-29404
Type: osv

## Affected
- Bitnami: `apache` — affected >=0 <2.4.54

## Details
In Apache HTTP Server 2.4.53 and earlier, a malicious request to a lua script that calls r:parsebody(0) may cause a denial of service due to no default limit on possible input size.

## References
- http://www.openwall.com/lists/oss-security/2022/06/08/5
- https://httpd.apache.org/security/vulnerabilities_24.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/7QUGG2QZWHTITMABFLVXA4DNYUOTPWYQ/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/YPY2BLEVJWFH34AX77ZJPLD2OOBYR6ND/
- https://security.gentoo.org/glsa/202208-20
- https://security.netapp.com/advisory/ntap-20220624-0005/
- https://nvd.nist.gov/vuln/detail/CVE-2022-29404
