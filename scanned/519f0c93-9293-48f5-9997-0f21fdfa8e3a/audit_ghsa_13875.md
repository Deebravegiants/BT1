# [H] Command injection in Apache Sling

## Summary
Severity: High
Advisory: GHSA-gvg3-83q4-rfhq
CVE: CVE-2023-25141
CWE: CWE-74
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2023-02-14
Source: https://github.com/advisories/GHSA-gvg3-83q4-rfhq
Type: github-advisory

## Affected
- Maven: `org.apache.sling:org.apache.sling.jcr.base` — affected >=0 <3.1.12

## Details
Apache Sling JCR Base < 3.1.12 has a critical injection vulnerability when running on old JDK versions (JDK 1.8.191 or earlier) through utility functions in RepositoryAccessor. The functions getRepository and getRepositoryFromURL allow an application to access data stored in a remote location via JDNI and RMI. Users of Apache Sling JCR Base are recommended to upgrade to Apache Sling JCR Base 3.1.12 or later, or to run on a more recent JDK.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-25141
- https://github.com/apache/sling-org-apache-sling-jcr-base/commit/6ed0a030fd5f13774aff0073c55cbe3ace0153cb
- https://github.com/apache/sling-org-apache-sling-jcr-base/commit/779d8a7dd0437a4f31de02c0d995afcf83b9904b
- https://github.com/apache/sling-org-apache-sling-jcr-base
- https://issues.apache.org/jira/browse/SLING-11770
- https://sling.apache.org/news.html
