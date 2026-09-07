# [M] Deserialization of Untrusted Data in Spring AMQP

## Summary
Severity: Medium
Advisory: GHSA-945q-ch46-pchg
CVE: CVE-2021-22095
CWE: CWE-502
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-12-01
Source: https://github.com/advisories/GHSA-945q-ch46-pchg
Type: github-advisory

## Affected
- Maven: `org.springframework.amqp:spring-amqp` — affected >=2.2.0 <2.2.20
- Maven: `org.springframework.amqp:spring-amqp` — affected >=2.3.0 <2.3.11

## Details
In Spring AMQP versions 2.2.0 - 2.2.19 and 2.3.0 - 2.3.11, the Spring AMQP Message object, in its toString() method, will create a new String object from the message body, regardless of its size. This can cause an OOM Error with a large message

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-22095
- https://github.com/spring-projects/spring-amqp/commit/bde294d62a8b7f3f1d5a9f50f862c6f0782efb9d
- https://tanzu.vmware.com/security/cve-2021-22097
