# [H] Apache Cassandra is vulnerable to privilege escalation in an mTLS environment using MutualTlsAuthenticator

## Summary
Severity: High
Advisory: GHSA-qxpc-96fq-wwmg
CVE: CVE-2026-27314
CWE: CWE-267
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-04-07
Source: https://github.com/advisories/GHSA-qxpc-96fq-wwmg
Type: github-advisory

## Affected
- Maven: `org.apache.cassandra:cassandra-all` — affected >=5.0-alpha1 <5.0.7

## Details
Privilege escalation in Apache Cassandra 5.0 on an mTLS environment using MutualTlsAuthenticator allows a user with only CREATE permission to associate their own certificate identity with an arbitrary role, including a superuser role, and authenticate as that role via ADD IDENTITY.

Users are recommended to upgrade to version 5.0.7+, which fixes this issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-27314
- https://github.com/apache/cassandra/commit/b584a435970e5125e1def5148d943c39569dc7af
- https://github.com/apache/cassandra
- https://github.com/apache/cassandra/releases/tag/cassandra-5.0.7
- https://lists.apache.org/thread/zrng82ddy4rpsmfyk582v6hqxcqrbz7f
- http://www.openwall.com/lists/oss-security/2026/04/07/7
