# [H] Apache Spark UI vulnerable to Command Injection

## Summary
Severity: High
Advisory: GHSA-59hw-j9g6-mfg3
CVE: CVE-2023-32007
CWE: CWE-77
Ecosystem: Maven, PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-05-02
Source: https://github.com/advisories/GHSA-59hw-j9g6-mfg3
Type: github-advisory

## Affected
- Maven: `org.apache.spark:spark-parent_2.12` — affected >=3.1.1 <3.2.2
- PyPI: `pyspark` — affected >=3.1.1 <3.2.2

## Details
The Apache Spark UI offers the possibility to enable ACLs via the configuration option spark.acls.enable. With an authentication filter, this checks whether a user has access permissions to view or modify the application. If ACLs are enabled, a code path in HttpSecurityFilter can allow someone to perform impersonation by providing an arbitrary user name. A malicious user might then be able to reach a permission check function that will ultimately build a Unix shell command based on their input, and execute it. This will result in arbitrary shell command execution as the user Spark is currently running as. This issue was disclosed earlier as CVE-2022-33891, but incorrectly claimed version 3.1.3 (which has since gone EOL) would not be affected.

NOTE: This vulnerability only affects products that are no longer supported by the maintainer.

Users are recommended to upgrade to a supported version of Apache Spark, such as version 3.4.0.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-32007
- https://github.com/apache/spark
- https://github.com/pypa/advisory-database/tree/main/vulns/pyspark/PYSEC-2023-72.yaml
- https://lists.apache.org/thread/poxgnxhhnzz735kr1wos366l5vdbb0nv
- https://spark.apache.org/security.html
- https://www.cve.org/CVERecord?id=CVE-2022-33891
- https://www.openwall.com/lists/oss-security/2023/05/02/1
- http://www.openwall.com/lists/oss-security/2023/05/02/1
