# [M] Apache Spark vulnerable to Log Injection

## Summary
Severity: Medium
Advisory: GHSA-43xg-8wmj-cw8h
CVE: CVE-2022-31777
CWE: CWE-74
Ecosystem: Maven, PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-11-01
Source: https://github.com/advisories/GHSA-43xg-8wmj-cw8h
Type: github-advisory

## Affected
- PyPI: `pyspark` — affected >=0 <3.2.2
- PyPI: `pyspark` — affected >=3.3.0 <3.3.1
- Maven: `org.apache.spark:spark-core_2.9.3` — affected >=0
- Maven: `org.apache.spark:spark-core_2.13` — affected >=0 <3.2.2
- Maven: `org.apache.spark:spark-core_2.13` — affected >=3.3.0 <3.3.1
- Maven: `org.apache.spark:spark-core_2.12` — affected >=0 <3.2.2
- Maven: `org.apache.spark:spark-core_2.12` — affected >=3.3.0 <3.3.1
- Maven: `org.apache.spark:spark-core_2.11` — affected >=0
- Maven: `org.apache.spark:spark-core_2.10` — affected >=0

## Details
A stored cross-site scripting (XSS) vulnerability in Apache Spark 3.2.1 and earlier, and 3.3.0, allows remote attackers to execute arbitrary JavaScript in the web browser of a user, by including a malicious payload into the logs which would be returned in logs rendered in the UI.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-31777
- https://github.com/apache/spark/commit/ad90195de56688ce0898691eb9d04297ab0871ad
- https://github.com/apache/spark
- https://github.com/pypa/advisory-database/tree/main/vulns/pyspark/PYSEC-2022-42976.yaml
- https://lists.apache.org/thread/60mgbswq2lsmrxykfxpqq13ztkm2ht6q
- https://web.archive.org/web/20220728105026/https://issues.apache.org/jira/browse/SPARK-39505
- http://www.openwall.com/lists/oss-security/2022/11/01/14
