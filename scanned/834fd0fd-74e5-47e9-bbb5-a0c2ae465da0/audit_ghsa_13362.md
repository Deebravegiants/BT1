# [C] RocketMQ NameServer component Code Injection vulnerability

## Summary
Severity: Critical
Advisory: GHSA-gpq8-963w-8qc9
CVE: CVE-2023-37582
CWE: CWE-94
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-07-12
Source: https://github.com/advisories/GHSA-gpq8-963w-8qc9
Type: github-advisory

## Affected
- Maven: `org.apache.rocketmq:rocketmq-namesrv` — affected >=0 <4.9.7
- Maven: `org.apache.rocketmq:rocketmq-namesrv` — affected >=5.0.0 <5.1.2

## Details
The RocketMQ NameServer component still has a remote command execution vulnerability as the CVE-2023-33246 issue was not completely fixed in version 5.1.1. 

When NameServer address are leaked on the extranet and lack permission verification, an attacker can exploit this vulnerability by using the update configuration function on the NameServer component to execute commands as the system users that RocketMQ is running as. 

It is recommended for users to upgrade their NameServer version to 5.1.2 or above for RocketMQ 5.x or 4.9.7 or above for RocketMQ 4.x to prevent these attacks.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-37582
- https://github.com/apache/rocketmq
- https://lists.apache.org/thread/m614czxtpvlztd7mfgcs2xcsg36rdbnc
- http://www.openwall.com/lists/oss-security/2023/07/12/1
