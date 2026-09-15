# [H] Pivotal RabbitMQ is vulnerable to a denial of service attack

## Summary
Severity: High
Advisory: GHSA-hrfh-7j5f-8ccr
CVE: CVE-2019-11287
CWE: CWE-134, CWE-400
Ecosystem: Hex
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-hrfh-7j5f-8ccr
Type: github-advisory

## Affected
- Hex: `RabbitMQ` — affected >=3.7.0 <3.7.21
- Hex: `RabbitMQ` — affected >=3.8.0 <3.8.1
- Hex: `RabbitMQ` — affected >=0 <1.16.7
- Hex: `RabbitMQ` — affected >=1.17.0 <1.17.4

## Details
Pivotal RabbitMQ, versions 3.7.x prior to 3.7.21 and 3.8.x prior to 3.8.1, and RabbitMQ for Pivotal Platform, 1.16.x versions prior to 1.16.7 and 1.17.x versions prior to 1.17.4, contain a web management plugin that is vulnerable to a denial of service attack. The "X-Reason" HTTP Header can be leveraged to insert a malicious Erlang format string that will expand and consume the heap, resulting in the server crashing.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-11287
- https://access.redhat.com/errata/RHSA-2020:0078
- https://github.com/DrunkenShells/Disclosures/tree/master/CVE-2019-11287-DoS%20via%20Heap%20Overflow-RabbitMQ%20Web%20Management%20Plugin
- https://github.com/rabbitmq/rabbitmq-server
- https://lists.debian.org/debian-lts-announce/2021/07/msg00011.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/EEQ6O7PMNJKYFMQYHAB55L423GYK63SO
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/PYTGR3D5FW2O25RXZOTIZMOD2HAUVBE4
- https://pivotal.io/security/cve-2019-11287
