# [M] Apache Zeppelin: LDAP injection in ActiveDirectoryGroupRealm filter construction

## Summary
Severity: Medium
Advisory: CVE-2026-44616
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:N)
Published: 2026-07-30
Source: https://osv.dev/vulnerability/CVE-2026-44616
Type: osv

## Details
LDAP injection vulnerability in Apache Zeppelin. ActiveDirectoryGroupRealm constructed LDAP search filters without escaping user-controlled input, allowing an authenticated attacker to inject LDAP filter syntax through the user-search endpoint                   and potentially expose directory information. The role-lookup path was also affected after successful LDAP authentication. This issue affects Apache Zeppelin versions 0.6.0 through 0.12.0. Users are recommended to upgrade to version 0.12.1, which                   fixes this issue.

## References
- http://www.openwall.com/lists/oss-security/2026/07/30/3
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/44xxx/CVE-2026-44616.json
- https://lists.apache.org/thread/p6llqpvcszpg1wc8kx5ncfkdbms3g0rn
- https://nvd.nist.gov/vuln/detail/CVE-2026-44616
- https://github.com/apache/zeppelin/pull/5226
