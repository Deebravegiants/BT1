# [M] Apache RocketMQ Vulnerable to Unauthorized Exposure of Sensitive Data

## Summary
Severity: Medium
Advisory: GHSA-q9w2-h4cw-8ghp
CVE: CVE-2024-23321
CWE: CWE-200
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2024-07-22
Source: https://github.com/advisories/GHSA-q9w2-h4cw-8ghp
Type: github-advisory

## Affected
- Maven: `org.apache.rocketmq:rocketmq-all` — affected >=4.5.2 <5.3.0

## Details
For RocketMQ versions 5.2.0 and below, under certain conditions, there is a risk of exposure of sensitive Information to an unauthorized actor even if RocketMQ is enabled with authentication and authorization functions.

An attacker, possessing regular user privileges or listed in the IP whitelist, could potentially acquire the administrator's account and password through specific interfaces. Such an action would grant them full control over RocketMQ, provided they have access to the broker IP address list.

To mitigate these security threats, it is strongly advised that users upgrade to version 5.3.0 or newer. Additionally, we recommend users to use RocketMQ ACL 2.0 instead of the original RocketMQ ACL when upgrading to version Apache RocketMQ 5.3.0.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-23321
- https://github.com/apache/rocketmq
- https://github.com/apache/rocketmq/releases/tag/rocketmq-all-5.3.0
- https://lists.apache.org/thread/lr8npobww786nrnddd1pcy974r17c830
- http://www.openwall.com/lists/oss-security/2024/07/22/1
