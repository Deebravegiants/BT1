# [M] Apache Superset Improper Input Validation vulnerability

## Summary
Severity: Medium
Advisory: GHSA-fm4q-j8g4-c9j4
CVE: CVE-2023-39265
CWE: CWE-20
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2023-09-06
Source: https://github.com/advisories/GHSA-fm4q-j8g4-c9j4
Type: github-advisory

## Affected
- PyPI: `apache-superset` — affected >=0

## Details
Apache Superset would allow for SQLite database connections to be incorrectly registered when an attacker uses alternative driver names like sqlite+pysqlite or by using database imports. This could allow for unexpected file creation on Superset webservers. Additionally, if Apache Superset is using a SQLite database for its metadata (not advised for production use) it could result in more severe vulnerabilities related to confidentiality and integrity. This vulnerability exists in Apache Superset versions up to and including 2.1.0.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-39265
- https://github.com/apache/superset
- https://lists.apache.org/thread/pwdzsdmv4g5g1n2h9m7ortfnxmhr7nfy
- http://packetstormsecurity.com/files/175094/Apache-Superset-2.0.0-Remote-Code-Execution.html
