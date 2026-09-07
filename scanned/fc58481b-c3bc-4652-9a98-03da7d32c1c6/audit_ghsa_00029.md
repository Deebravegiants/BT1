# [C] Exposure of Sensitive Information in Hadoop

## Summary
Severity: Critical
Advisory: GHSA-mq8p-h798-xcrp
CVE: CVE-2017-15718
CWE: CWE-200
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2018-12-21
Source: https://github.com/advisories/GHSA-mq8p-h798-xcrp
Type: github-advisory

## Affected
- Maven: `org.apache.hadoop:hadoop-main` — affected >=2.7.3 <2.7.5

## Details
The YARN NodeManager in Apache Hadoop 2.7.3 and 2.7.4 can leak the password for credential store provider used by the NodeManager to YARN Applications.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-15718
- https://github.com/advisories/GHSA-mq8p-h798-xcrp
- https://lists.apache.org/thread.html/773c93c2d8a6a52bbe97610c2b1c2ad205b970e1b8c04fb5b2fccad6@%3Cgeneral.hadoop.apache.org%3E
