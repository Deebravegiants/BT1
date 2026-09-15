# [M] Apache Airflow FAB Auth Manager contains an LDAP filter injection vulnerability

## Summary
Severity: Medium
Advisory: GHSA-g283-w6fp-c4fc
CVE: CVE-2026-46745
CWE: CWE-90
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-05-26
Source: https://github.com/advisories/GHSA-g283-w6fp-c4fc
Type: github-advisory

## Affected
- PyPI: `apache-airflow-providers-fab` — affected >=0 <3.6.4

## Details
Apache Airflow FAB Auth Manager contains an LDAP filter injection vulnerability (CWE-90) that allows unauthenticated attackers to exfiltrate directory data or bypass authentication. Upgrade to apache-airflow-providers-fab 3.6.4 or later. If immediate upgrade is not possible, disable LDAP authentication until the provider can be updated.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-46745
- https://github.com/apache/airflow/pull/66417
- https://github.com/apache/airflow/commit/3f7756bea71a7c7988511ec0557314ffb15fbe5e
- https://github.com/apache/airflow
- https://lists.apache.org/thread/dvfy0bs181xwsrjrd3y5c55ztbzm8yhh
- http://www.openwall.com/lists/oss-security/2026/05/24/10
