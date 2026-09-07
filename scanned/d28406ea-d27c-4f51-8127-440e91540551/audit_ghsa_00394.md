# [H] Akka Java Serialization vulnerability

## Summary
Severity: High
Advisory: GHSA-mm57-9j6q-rxm2
CVE: CVE-2017-1000034
CWE: CWE-502
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2018-10-22
Source: https://github.com/advisories/GHSA-mm57-9j6q-rxm2
Type: github-advisory

## Affected
- Maven: `com.typesafe.akka:akka-actor` — affected >=0 <2.4.17

## Details
Akka versions <=2.4.16 and 2.5-M1 are vulnerable to a java deserialization attack in its Remoting component resulting in remote code execution in the context of the ActorSystem.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-1000034
- https://github.com/akka/akka/issues/22283
- https://github.com/akka/akka/commit/cc6561b47e5958923df520b8a9514010d3e11d49
- https://github.com/advisories/GHSA-mm57-9j6q-rxm2
- http://doc.akka.io/docs/akka/2.4/security/2017-02-10-java-serialization.html
