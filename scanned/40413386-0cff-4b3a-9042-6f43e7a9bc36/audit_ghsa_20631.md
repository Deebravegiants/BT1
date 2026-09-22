# [C] Apache Hadoop argument injection vulnerability

## Summary
Severity: Critical
Advisory: GHSA-8wm5-8h9c-47pc
CVE: CVE-2022-25168
CWE: CWE-78, CWE-88
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-08-05
Source: https://github.com/advisories/GHSA-8wm5-8h9c-47pc
Type: github-advisory

## Affected
- Maven: `org.apache.hadoop:hadoop-common` — affected >=2.0.0 <2.10.2
- Maven: `org.apache.hadoop:hadoop-common` — affected >=3.0.0-alpha <3.2.4
- Maven: `org.apache.hadoop:hadoop-common` — affected >=3.3.0 <3.3.3

## Details
Apache Hadoop's `FileUtil.unTar(File, File)` API does not escape the input file name before being passed to the shell. An attacker can inject arbitrary commands. This is only used in Hadoop 3.3 InMemoryAliasMap.completeBootstrapTransfer, which is only ever run by a local user. It has been used in Hadoop 2.x for yarn localization, which does enable remote code execution. It is used in Apache Spark, from the SQL command ADD ARCHIVE. As the ADD ARCHIVE command adds new binaries to the classpath, being able to execute shell scripts does not confer new permissions to the caller. SPARK-38305. "Check existence of file before untarring/zipping", which is included in 3.3.0, 3.1.4, 3.2.2, prevents shell commands being executed, regardless of which version of the hadoop libraries are in use. Users should upgrade to Apache Hadoop 2.10.2, 3.2.4, 3.3.3 or upper (including HADOOP-18136).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-25168
- https://github.com/apache/hadoop/commit/cae749b076f35f0be13a926ee8cfbb7ce4402746
- https://github.com/apache/hadoop
- https://lists.apache.org/thread/mxqnb39jfrwgs3j6phwvlrfq4mlox130
- https://security.netapp.com/advisory/ntap-20220915-0007
