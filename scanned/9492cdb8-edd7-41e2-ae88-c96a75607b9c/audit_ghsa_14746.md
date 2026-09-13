# [H] Apache Hive and Spark: CookieSigner exposes the correct signature when message verification fails

## Summary
Severity: High
Advisory: GHSA-77pm-w3hx-f8mj
CVE: CVE-2024-23945
CWE: CWE-209
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2024-12-23
Source: https://github.com/advisories/GHSA-77pm-w3hx-f8mj
Type: github-advisory

## Affected
- Maven: `org.apache.hive:hive-service` — affected >=1.2.0 <4.0.0
- Maven: `org.apache.spark:spark-hive-thriftserver_2.11` — affected >=0
- Maven: `org.apache.spark:spark-hive-thriftserver_2.12` — affected >=0 <3.4.2

## Details
Signing cookies is an application security feature that adds a digital signature to cookie data to verify its authenticity and integrity. The signature helps prevent malicious actors from modifying the cookie value, which can lead to security vulnerabilities and exploitation. Apache Hive’s service component accidentally exposes the signed cookie to the end user when there is a mismatch in signature between the current and expected cookie. Exposing the correct cookie signature can lead to further exploitation.

The vulnerable CookieSigner logic was introduced in Apache Hive by HIVE-9710 (1.2.0) and in Apache Spark by SPARK-14987 (2.0.0). The affected components are the following:
* org.apache.hive:hive-service
* org.apache.spark:spark-hive-thriftserver_2.11
* org.apache.spark:spark-hive-thriftserver_2.12

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-23945
- https://github.com/apache/hive/commit/7638cb1a3b07713cc490aa2909a37037f89e08b4
- https://github.com/apache/spark/commit/cf59b1f51c16301f689b4e0f17ba4dbd140e1b19
- https://github.com/apache/hive
- https://github.com/apache/spark
- https://issues.apache.org/jira/browse/HIVE-9710
- https://issues.apache.org/jira/browse/SPARK-14987
- https://lists.apache.org/thread/59r4mv7glrxpwkkdjvjbdljfpx3f5zzc
- https://lists.apache.org/thread/5o2ljnzrv8zvhjw9vy7b4rwjpc32hgfc
- http://www.openwall.com/lists/oss-security/2024/12/23/2
