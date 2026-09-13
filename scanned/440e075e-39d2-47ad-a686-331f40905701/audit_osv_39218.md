# [M] Apache Zeppelin: LDAP filter injection in LdapRealm — incomplete fix of CVE-2024-31867

## Summary
Severity: Medium
Advisory: CVE-2026-44617
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N)
Published: 2026-07-30
Source: https://osv.dev/vulnerability/CVE-2026-44617
Type: osv

## Details
LDAP filter injection vulnerability in Apache Zeppelin. LdapRealm used RFC 4514 distinguished-name escaping when constructing LDAP search filters instead of RFC 4515 filter escaping, leaving special filter characters insufficiently escaped.                   This is an incomplete fix of CVE-2024-31867. This issue affects Apache Zeppelin versions 0.11.1, 0.11.2, and 0.12.0. Users are recommended to upgrade to version 0.12.1, which fixes this issue.

## References
- https://www.cve.org/CVERecord?id=CVE-2024-31867
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/44xxx/CVE-2026-44617.json
- https://lists.apache.org/thread/s65t6n3s1v4j5b1w7zvv5w73ko69m1zv
- https://nvd.nist.gov/vuln/detail/CVE-2026-44617
- https://github.com/apache/zeppelin/pull/5226
