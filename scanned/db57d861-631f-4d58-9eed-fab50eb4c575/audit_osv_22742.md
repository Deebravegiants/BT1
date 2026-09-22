# [H] The software is vulnerable when using LDAP-based authentication in YCQL with Microsoft’s Active Directory

## Summary
Severity: High
Advisory: CVE-2022-37397
CVSS: 8.3 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:L)
Published: 2022-08-12
Source: https://osv.dev/vulnerability/CVE-2022-37397
Type: osv

## Details
An issue was discovered in the YugabyteDB 2.6.1 when using LDAP-based authentication in YCQL with Microsoft’s Active Directory. When anonymous or unauthenticated LDAP binding is enabled, it allows bypass of authentication with an empty password.

## References
- https://www.yugabyte.com/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/37xxx/CVE-2022-37397.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-37397
