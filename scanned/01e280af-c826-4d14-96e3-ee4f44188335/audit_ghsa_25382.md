# [H] Insecure Inherited Permissions in  Apache Hadoop

## Summary
Severity: High
Advisory: GHSA-mf7c-35mq-75pj
CVE: CVE-2016-6811
CWE: CWE-277
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-mf7c-35mq-75pj
Type: github-advisory

## Affected
- Maven: `org.apache.hadoop:hadoop-common` — affected >=2.0.0-alpha <2.7.4

## Details
In Apache Hadoop 2.x before 2.7.4, a user who can escalate to yarn user can possibly run arbitrary commands as root user.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-6811
- https://lists.apache.org/thread.html/9ba3c12bbdfd5b2cae60909e48f92608e00c8d99196390b8cfeca307@%3Cgeneral.hadoop.apache.org%3E
