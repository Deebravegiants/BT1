# [M] Directory traversal in Apache RocketMQ

## Summary
Severity: Medium
Advisory: GHSA-5x3v-2gxr-59m2
CVE: CVE-2019-17572
CWE: CWE-22
Ecosystem: Maven
Published: 2020-07-01
Source: https://github.com/advisories/GHSA-5x3v-2gxr-59m2
Type: github-advisory

## Affected
- Maven: `org.apache.rocketmq:rocketmq-broker` — affected >=4.2.0 <4.6.1

## Details
In Apache RocketMQ 4.2.0 to 4.6.0, when the automatic topic creation in the broker is turned on by default, an evil topic like “../../../../topic2020” is sent from rocketmq-client to the broker, a topic folder will be created in the parent directory in brokers, which leads to a directory traversal vulnerability. Users of the affected versions should apply one of the following: Upgrade to Apache RocketMQ 4.6.1 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-17572
- https://github.com/apache/rocketmq/issues/1637
- https://github.com/apache/rocketmq/commit/f8f6fbe4aa7f5dee937e688322628c366b12a552
- https://lists.apache.org/thread.html/fdea1c5407da47a17d5522fa149a097cacded1916c1c1534d46edc6d%40%3Cprivate.rocketmq.apache.org%3E
- https://seclists.org/oss-sec/2020/q2/112
- https://snyk.io/vuln/SNYK-JAVA-ORGAPACHEROCKETMQ-569108
