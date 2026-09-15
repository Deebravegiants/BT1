# [C] Apache RocketMQ may have remote code execution vulnerability when using update configuration function

## Summary
Severity: Critical
Advisory: GHSA-x3cq-8f32-5f63
CVE: CVE-2023-33246
CWE: CWE-94
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H/E:H (CVSS_V3)
Published: 2023-07-06
Source: https://github.com/advisories/GHSA-x3cq-8f32-5f63
Type: github-advisory

## Affected
- Maven: `org.apache.rocketmq:rocketmq-broker` — affected >=5.0.0 <5.1.1
- Maven: `org.apache.rocketmq:rocketmq-namesrv` — affected >=4.0.0 <4.9.6
- Maven: `org.apache.rocketmq:rocketmq-controller` — affected >=5.0.0 <5.1.1
- Maven: `org.apache.rocketmq:rocketmq-namesrv` — affected >=5.0.0 <5.1.1

## Details
For RocketMQ versions 5.1.0 and below, under certain conditions, there is a risk of remote command execution. 

Several components of RocketMQ, including NameServer, Broker, and Controller, are leaked on the extranet and lack permission verification, an attacker can exploit this vulnerability by using the update configuration function to execute commands as the system users that RocketMQ is running as. Additionally, an attacker can achieve the same effect by forging the RocketMQ protocol content. 

To prevent these attacks, users are recommended to upgrade to version 5.1.1 or above for using RocketMQ 5.x or 4.9.6 or above for using RocketMQ 4.x .

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-33246
- https://github.com/apache/rocketmq/commit/9d411cf04a695e7a3f41036e8377b0aa544d754d
- https://github.com/apache/rocketmq/commit/c3ada731405c5990c36bf58d50b3e61965300703
- https://github.com/Malayke/CVE-2023-33246_RocketMQ_RCE_EXPLOIT
- https://github.com/apache/rocketmq
- https://github.com/jakabakos/CVE-2023-33246_Apache_RocketMQ_RCE
- https://lists.apache.org/thread/1s8j2c8kogthtpv3060yddk03zq0pxyp
- https://www.cisa.gov/known-exploited-vulnerabilities-catalog?field_cve=CVE-2023-33246
- https://www.vicarius.io/vsociety/posts/rocketmq-rce-cve-2023-33246-33247
- http://packetstormsecurity.com/files/173339/Apache-RocketMQ-5.1.0-Arbitrary-Code-Injection.html
- http://www.openwall.com/lists/oss-security/2023/07/12/1
