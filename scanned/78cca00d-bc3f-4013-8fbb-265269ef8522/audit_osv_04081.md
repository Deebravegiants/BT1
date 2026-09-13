# [H] mod_sed denial of service

## Summary
Severity: High
Advisory: BIT-apache-2022-30522
Aliases: CVE-2022-30522
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-apache-2022-30522
Type: osv

## Affected
- Bitnami: `apache` — affected >=2.4.53 <2.4.54

## Details
If Apache HTTP Server 2.4.53 is configured to do transformations with mod_sed in contexts where the input to mod_sed may be very large, mod_sed may make excessively large memory allocations and trigger an abort.

## References
- http://www.openwall.com/lists/oss-security/2022/06/08/6
- https://httpd.apache.org/security/vulnerabilities_24.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/7QUGG2QZWHTITMABFLVXA4DNYUOTPWYQ/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/YPY2BLEVJWFH34AX77ZJPLD2OOBYR6ND/
- https://security.gentoo.org/glsa/202208-20
- https://security.netapp.com/advisory/ntap-20220624-0005/
- https://nvd.nist.gov/vuln/detail/CVE-2022-30522
