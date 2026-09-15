# [H] Information Disclosure in mod_lua with websockets

## Summary
Severity: High
Advisory: BIT-apache-2022-30556
Aliases: CVE-2022-30556
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-apache-2022-30556
Type: osv

## Affected
- Bitnami: `apache` — affected >=0 <2.4.54

## Details
Apache HTTP Server 2.4.53 and earlier may return lengths to applications calling r:wsread() that point past the end of the storage allocated for the buffer.

## References
- http://www.openwall.com/lists/oss-security/2022/06/08/7
- https://httpd.apache.org/security/vulnerabilities_24.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/7QUGG2QZWHTITMABFLVXA4DNYUOTPWYQ/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/YPY2BLEVJWFH34AX77ZJPLD2OOBYR6ND/
- https://security.gentoo.org/glsa/202208-20
- https://security.netapp.com/advisory/ntap-20220624-0005/
- https://nvd.nist.gov/vuln/detail/CVE-2022-30556
