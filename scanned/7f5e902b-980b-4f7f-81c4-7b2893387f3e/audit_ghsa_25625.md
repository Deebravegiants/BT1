# [C] Path traversal in Hadoop

## Summary
Severity: Critical
Advisory: GHSA-gx2c-fvhc-ph4j
CVE: CVE-2022-26612
CWE: CWE-22
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-04-08
Source: https://github.com/advisories/GHSA-gx2c-fvhc-ph4j
Type: github-advisory

## Affected
- Maven: `org.apache.hadoop:hadoop-common` — affected >=3.2.0 <3.2.3
- Maven: `org.apache.hadoop:hadoop-common` — affected >=0 <2.10.2
- Maven: `org.apache.hadoop:hadoop-common` — affected >=3.3.0 <3.3.3

## Details
In Apache Hadoop, The unTar function uses unTarUsingJava function on Windows and the built-in tar utility on Unix and other OSes. As a result, a TAR entry may create a symlink under the expected extraction directory which points to an external directory. A subsequent TAR entry may extract an arbitrary file into the external directory using the symlink name. This however would be caught by the same targetDirPath check on Unix because of the getCanonicalPath call. However on Windows, getCanonicalPath doesn't resolve symbolic links, which bypasses the check. unpackEntries during TAR extraction follows symbolic links which allows writing outside expected base directory on Windows. This was addressed in Apache Hadoop 2.10.2, 3.2.3, 3.3.3, and 3.4.0.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-26612
- https://github.com/apache/hadoop
- https://github.com/apache/hadoop/commits/rel/release-2.10.2/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/FileUtil.java
- https://github.com/apache/hadoop/commits/rel/release-3.2.3/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/FileUtil.java
- https://github.com/apache/hadoop/commits/rel/release-3.3.3/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/FileUtil.java
- https://github.com/apache/hadoop/commits/rel/release-3.4.0/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/FileUtil.java
- https://issues.apache.org/jira/browse/HADOOP-18317
- https://lists.apache.org/thread/hslo7wzw2449gv1jyjk8g6ttd7935fyz
- https://security.netapp.com/advisory/ntap-20220519-0004
