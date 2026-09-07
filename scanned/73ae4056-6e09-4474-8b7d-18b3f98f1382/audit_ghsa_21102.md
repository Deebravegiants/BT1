# [H] Apache Hive before 3.1.3 `CREATE` and `DROP` function operations do not check for necessary authorization.

## Summary
Severity: High
Advisory: GHSA-v3p8-j597-3xg8
CVE: CVE-2021-34538
CWE: CWE-306
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-07-17
Source: https://github.com/advisories/GHSA-v3p8-j597-3xg8
Type: github-advisory

## Affected
- Maven: `org.apache.hive:hive` — affected >=0 <3.1.3

## Details
Apache Hive before 3.1.3 `CREATE` and `DROP` function operations do not check for necessary authorization of involved entities in the query. It was found that an unauthorized user can manipulate an existing UDF without having the privileges to do so. This allowed unauthorized or underprivileged users to drop and recreate UDFs pointing them to new jars that could be potentially malicious.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-34538
- https://github.com/apache/hive
- https://lists.apache.org/thread/oqqgnhz4c6nxsfd0xstosnk0g15f7354
