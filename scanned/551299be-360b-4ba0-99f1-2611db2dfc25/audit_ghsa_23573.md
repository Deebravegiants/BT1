# [M] Improper Authentication in Apache Kafka

## Summary
Severity: Medium
Advisory: GHSA-xm78-4m3g-7wm7
CVE: CVE-2017-12610
CWE: CWE-287
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-xm78-4m3g-7wm7
Type: github-advisory

## Affected
- Maven: `org.apache.kafka:kafka-clients` — affected >=0.10.0.0 <0.10.2.2
- Maven: `org.apache.kafka:kafka-clients` — affected >=0.11.0.0 <0.11.0.2

## Details
In Apache Kafka 0.10.0.0 to 0.10.2.1 and 0.11.0.0 to 0.11.0.1, authenticated Kafka clients may use impersonation via a manually crafted protocol message with SASL/PLAIN or SASL/SCRAM authentication when using the built-in PLAIN or SCRAM server implementations in Apache Kafka.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-12610
- https://lists.apache.org/thread.html/519eb0fd45642dcecd9ff74cb3e71c20a4753f7d82e2f07864b5108f@%3Cdev.drill.apache.org%3E
- https://lists.apache.org/thread.html/b0656d359c7d40ec9f39c8cc61bca66802ef9a2a12ee199f5b0c1442@%3Cdev.drill.apache.org%3E
- https://lists.apache.org/thread.html/b6157be1a09df332294213bd21e90dcf9fe4c1810193be54620e4210@%3Cusers.kafka.apache.org%3E
- https://lists.apache.org/thread.html/f9bc3e55f4e28d1dcd1a69aae6d53e609a758e34d2869b4d798e13cc@%3Cissues.drill.apache.org%3E
- https://www.oracle.com/security-alerts/cpujul2020.html
- http://www.securityfocus.com/bid/104899
