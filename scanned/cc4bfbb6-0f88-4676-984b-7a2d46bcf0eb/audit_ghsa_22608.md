# [M] PostgreSQL PL/Java Improper Privilege Management

## Summary
Severity: Medium
Advisory: GHSA-837x-xww6-7jqm
CVE: CVE-2016-0767
CWE: CWE-269
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-837x-xww6-7jqm
Type: github-advisory

## Affected
- Maven: `postgresql:pljava-public` — affected >=0 <1.5.0

## Details
PostgreSQL PL/Java before 1.5.0 allows remote authenticated users with USAGE permission on the public schema to alter the public schema classpath.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-0767
- https://github.com/tada/pljava
- https://tada.github.io/pljava/releasenotes-pre1_6.html#PL.2FJava_1.5.0_.2829_March_2016.29
