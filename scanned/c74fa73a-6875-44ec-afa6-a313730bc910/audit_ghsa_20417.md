# [M] Improper Input Validation and Injection in Apache Log4j2

## Summary
Severity: Medium
Advisory: GHSA-8489-44mv-ggj8
CVE: CVE-2021-44832
CWE: CWE-20, CWE-74
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:H/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-01-04
Source: https://github.com/advisories/GHSA-8489-44mv-ggj8
Type: github-advisory

## Affected
- Maven: `org.apache.logging.log4j:log4j-core` — affected >=2.0-beta7 <2.3.2
- Maven: `org.apache.logging.log4j:log4j-core` — affected >=2.4 <2.12.4
- Maven: `org.apache.logging.log4j:log4j-core` — affected >=2.13.0 <2.17.1
- Maven: `org.ops4j.pax.logging:pax-logging-log4j2` — affected >=1.8.0 <1.9.2
- Maven: `org.ops4j.pax.logging:pax-logging-log4j2` — affected >=1.10.0 <1.10.9
- Maven: `org.ops4j.pax.logging:pax-logging-log4j2` — affected >=1.11.0 <1.11.13
- Maven: `org.ops4j.pax.logging:pax-logging-log4j2` — affected >=2.0.0 <2.0.14

## Details
Apache Log4j2 versions 2.0-beta7 through 2.17.0 (excluding security fix releases 2.3.2 and 2.12.4) are vulnerable to an attack where an attacker with permission to modify the logging configuration file can construct a malicious configuration using a JDBC Appender with a data source referencing a JNDI URI which can execute remote code. This issue is fixed by limiting JNDI data source names to the java protocol in Log4j2 versions 2.17.1, 2.12.4, and 2.3.2.


# Affected packages
Only the `org.apache.logging.log4j:log4j-core` package is directly affected by this vulnerability. The `org.apache.logging.log4j:log4j-api` should be kept at the same version as the `org.apache.logging.log4j:log4j-core` package to ensure compatability if in use.

This issue does not impact default configurations of Log4j2 and requires an attacker to have control over the Log4j2 configuration, which reduces the likelihood of being exploited.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-44832
- https://cert-portal.siemens.com/productcert/pdf/ssa-784507.pdf
- https://github.com/apache/logging-log4j2
- https://issues.apache.org/jira/browse/LOG4J2-3293
- https://lists.apache.org/thread/s1o5vlo78ypqxnzn6p8zf6t9shtq5143
- https://lists.debian.org/debian-lts-announce/2021/12/msg00036.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/EVV25FXL4FU5X6X5BSL7RLQ7T6F65MRA
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/T57MPJUW3MA6QGWZRTMCHHMMPQNVKGFC
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/EVV25FXL4FU5X6X5BSL7RLQ7T6F65MRA
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/T57MPJUW3MA6QGWZRTMCHHMMPQNVKGFC
- https://sec.cloudapps.cisco.com/security/center/content/CiscoSecurityAdvisory/cisco-sa-apache-log4j-qRuKNEbd
- https://security.netapp.com/advisory/ntap-20220104-0001
- https://tools.cisco.com/security/center/content/CiscoSecurityAdvisory/cisco-sa-apache-log4j-qRuKNEbd
- https://www.oracle.com/security-alerts/cpuapr2022.html
- https://www.oracle.com/security-alerts/cpujan2022.html
- https://www.oracle.com/security-alerts/cpujul2022.html
- http://www.openwall.com/lists/oss-security/2021/12/28/1
