# [M] Apache Cassandra: Authenticated DoS via ALTER ROLE Password Hashing

## Summary
Severity: Medium
Advisory: CVE-2026-32588
Aliases: GHSA-qffm-gf3j-6mvg
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-04-07
Source: https://osv.dev/vulnerability/CVE-2026-32588
Type: osv

## Details
Authenticated DoS over CQL in Apache Cassandra 4.0, 4.1, 5.0 allows authenticated user to raise query latencies via repeated password changes.
Users are recommended to upgrade to version 4.0.20, 4.1.11, 5.0.7, which fixes this issue.

## References
- http://www.openwall.com/lists/oss-security/2026/04/07/9
- https://repo.maven.apache.org/maven2/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/32xxx/CVE-2026-32588.json
- https://lists.apache.org/thread/2tnwjdnss378glxrsmnlzz3k53ftphrc
- https://nvd.nist.gov/vuln/detail/CVE-2026-32588
