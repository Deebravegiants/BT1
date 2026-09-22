# [C] Apache Ignite: Possible RCE when deserializing incoming messages by the server node

## Summary
Severity: Critical
Advisory: GHSA-8355-xj3p-hv6q
CVE: CVE-2024-52577
CWE: CWE-502
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2025-02-14
Source: https://github.com/advisories/GHSA-8355-xj3p-hv6q
Type: github-advisory

## Affected
- Maven: `org.apache.ignite:ignite-core` — affected >=2.6.0 <2.17.0

## Details
In Apache Ignite versions from 2.6.0 and before 2.17.0, configured Class Serialization Filters are ignored for some Ignite endpoints. The vulnerability could be exploited if an attacker manually crafts an Ignite message containing a vulnerable object whose class is present in the Ignite server classpath and sends it to Ignite server endpoints. Deserialization of such a message by the Ignite server may result in the execution of arbitrary code on the Apache Ignite server side.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-52577
- https://github.com/apache/ignite/commit/f1d3579eabb2c6f5b11b94d58600afc497a8603d
- https://github.com/apache/ignite
- https://lists.apache.org/thread/1bst0n27m9kb3b6f6hvlghn182vqb2hh
- http://www.openwall.com/lists/oss-security/2025/02/14/2
