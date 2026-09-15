# [H] Apache Spark UI can allow impersonation if ACLs enabled

## Summary
Severity: High
Advisory: GHSA-4x9r-j582-cgr8
CVE: CVE-2022-33891
CWE: CWE-78
Ecosystem: Maven, PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H/E:H (CVSS_V3)
Published: 2022-07-19
Source: https://github.com/advisories/GHSA-4x9r-j582-cgr8
Type: github-advisory

## Affected
- Maven: `org.apache.spark:spark-parent_2.12` — affected >=0
- Maven: `org.apache.spark:spark-parent_2.12` — affected >=3.1.1 <3.2.2
- PyPI: `pyspark` — affected >=0 <3.1.3
- PyPI: `pyspark` — affected >=3.2.0 <3.2.2

## Details
The Apache Spark UI offers the possibility to enable ACLs via the configuration option `spark.acls.enable`. With an authentication filter, this checks whether a user has access permissions to view or modify the application. If ACLs are enabled, a code path in HttpSecurityFilter can allow someone to perform impersonation by providing an arbitrary user name. A malicious user might then be able to reach a permission check function that will ultimately build a Unix shell command based on their input, and execute it. This will result in arbitrary shell command execution as the user Spark is currently running as. This affects Apache Spark versions 3.0.3 and earlier, versions 3.1.1 to 3.1.2, and versions 3.2.0 to 3.2.1.

A previous version of this advisory incorrectly stated that version 3.1.3 was not vulnerable. Per [GHSA-59hw-j9g6-mfg3](https://github.com/advisories/GHSA-59hw-j9g6-mfg3), version 3.1.3 is vulnerable and vulnerable version ranges in this advisory have been changed to reflect the correct information.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-33891
- https://github.com/apache/spark
- https://github.com/pypa/advisory-database/tree/main/vulns/pyspark/PYSEC-2022-236.yaml
- https://lists.apache.org/thread/p847l3kopoo5bjtmxrcwk21xp6tjxqlc
- https://packetstormsecurity.com/files/168309/Apache-Spark-Unauthenticated-Command-Injection.html
- https://www.cisa.gov/known-exploited-vulnerabilities-catalog?field_cve=CVE-2022-33891
- https://www.openwall.com/lists/oss-security/2023/05/02/1
- http://packetstormsecurity.com/files/168309/Apache-Spark-Unauthenticated-Command-Injection.html
- http://www.openwall.com/lists/oss-security/2023/05/02/1
