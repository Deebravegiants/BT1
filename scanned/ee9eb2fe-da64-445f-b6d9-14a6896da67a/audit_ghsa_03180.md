# [M] Command injection in Apache Flink

## Summary
Severity: Medium
Advisory: GHSA-6g88-99wj-8mgg
CVE: CVE-2020-1960
CWE: CWE-74
Ecosystem: Maven
CVSS: CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2021-05-21
Source: https://github.com/advisories/GHSA-6g88-99wj-8mgg
Type: github-advisory

## Affected
- Maven: `org.apache.flink:flink-core` — affected >=0 <1.9.3
- Maven: `org.apache.flink:flink-core` — affected >=1.10.0 <1.10.1

## Details
A vulnerability in Apache Flink where, when running a process with an enabled JMXReporter, with a port configured via metrics.reporter.reporter_name>.port, an attacker with local access to the machine and JMX port can execute a man-in-the-middle attack using a specially crafted request to rebind the JMXRMI registry to one under the attacker's control. This compromises any connection established to the process via JMX, allowing extraction of credentials and any other transferred data.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-1960
- https://lists.apache.org/thread.html/r23e559dee1e69741557b5fe431846de1f1a5981356d0ddb9482df88a%40%3Cdev.flink.apache.org%3E
- https://lists.apache.org/thread.html/r26fcdd4fe288323006253437ebc4dd6fdfadfb5e93465a0e4f68420d@%3Cuser-zh.flink.apache.org%3E
- https://lists.apache.org/thread.html/r28f17e564950d663e68cc6fe75756012dda62ac623766bb9bc5e7034@%3Cissues.flink.apache.org%3E
- https://lists.apache.org/thread.html/r663cf0d5c386bba2f562d45ad484d786151a84f0b95e45e2b0fb8e50@%3Cissues.flink.apache.org%3E
