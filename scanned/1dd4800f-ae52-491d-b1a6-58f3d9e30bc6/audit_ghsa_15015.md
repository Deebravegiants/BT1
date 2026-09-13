# [M] Apache Superset server arbitrary file read 

## Summary
Severity: Medium
Advisory: GHSA-hcr7-cqwc-q5gq
CVE: CVE-2024-34693
CWE: CWE-20
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2024-06-20
Source: https://github.com/advisories/GHSA-hcr7-cqwc-q5gq
Type: github-advisory

## Affected
- PyPI: `apache-superset` — affected >=0 <3.1.3
- PyPI: `apache-superset` — affected >=4.0.0 <4.0.1

## Details
Improper Input Validation vulnerability in Apache Superset, allows for an authenticated attacker to create a MariaDB connection with local_infile enabled. If both the MariaDB server (off by default) and the local mysql client on the web server are set to allow for local infile, it's possible for the attacker to execute a specific MySQL/MariaDB SQL command that is able to read files from the server and insert their content on a MariaDB database table. This issue affects Apache Superset before version 3.1.3 and in version 4.0.0.

Users are recommended to upgrade to version 4.0.1 or 3.1.3, both of which fix the issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-34693
- https://github.com/apache/superset
- https://lists.apache.org/thread/1803x1s34m7r71h1k0q1njol8k6fmyon
- http://www.openwall.com/lists/oss-security/2024/06/20/1
