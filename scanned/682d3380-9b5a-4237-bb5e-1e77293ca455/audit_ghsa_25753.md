# [C] Deserializer tampering in Apache Dubbo

## Summary
Severity: Critical
Advisory: GHSA-v2rg-8cwr-75g8
CVE: CVE-2021-25641
CWE: CWE-502
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-03-18
Source: https://github.com/advisories/GHSA-v2rg-8cwr-75g8
Type: github-advisory

## Affected
- Maven: `org.apache.dubbo:dubbo` — affected >=2.5.0 <2.7.8
- Maven: `com.alibaba:dubbo` — affected >=2.5.0 <2.6.9

## Details
Each Apache Dubbo server will set a serialization id to tell the clients which serialization protocol it is working on. But for Dubbo versions before 2.7.8 or 2.6.9, an attacker can choose which serialization id the Provider will use by tampering with the byte preamble flags, aka, not following the server's instruction. This means that if a weak deserializer such as the Kryo and FST are somehow in code scope (e.g. if Kryo is somehow a part of a dependency), a remote unauthenticated attacker can tell the Provider to use the weak deserializer, and then proceed to exploit it.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-25641
- https://lists.apache.org/thread.html/r99ef7fa35585d3a68762de07e8d2b2bc48b8fa669a03e8d84b9673f3%40%3Cdev.dubbo.apache.org%3E
