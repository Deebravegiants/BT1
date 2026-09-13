# [H] Apache Superset: SQLLab Improper readonly query validation allows unauthorized write access

## Summary
Severity: High
Advisory: GHSA-787v-v9vq-4rgv
CVE: CVE-2024-55633
CWE: CWE-285, CWE-863
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2024-12-12
Source: https://github.com/advisories/GHSA-787v-v9vq-4rgv
Type: github-advisory

## Affected
- PyPI: `apache-superset` — affected >=0 <4.1.0

## Details
Improper Authorization vulnerability in Apache Superset. On Postgres analytic databases an attacker with SQLLab access can craft a specially designed SQL DML statement that is Incorrectly identified as a read-only query, enabling its execution. Non postgres analytics database connections and postgres analytics database connections set with a readonly user (advised) are not vulnerable. 

This issue affects Apache Superset: before 4.1.0.

Users are recommended to upgrade to version 4.1.0, which fixes the issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-55633
- https://github.com/apache/superset
- https://lists.apache.org/thread/bwmd17fcvljt9q4cgctp4v09zh3qs7fb
- http://www.openwall.com/lists/oss-security/2024/12/12/1
