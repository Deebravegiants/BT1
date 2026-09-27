# [C] Scala subject to file deletion, code execution due to Java deserialization chain with LazyList object deserialization

## Summary
Severity: Critical
Advisory: GHSA-8qv5-68g4-248j
CVE: CVE-2022-36944
CWE: CWE-502
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-09-25
Source: https://github.com/advisories/GHSA-8qv5-68g4-248j
Type: github-advisory

## Affected
- Maven: `org.scala-lang:scala-library` — affected >=2.13.0 <2.13.9

## Details
Scala 2.13.x before 2.13.9 has a Java deserialization chain in its JAR file. On its own, it cannot be exploited. There is only a risk in conjunction with LazyList object deserialization within an application. In such situations, it allows attackers to erase contents of arbitrary files, make network connections, or possibly run arbitrary code (specifically, Function0 functions) via a gadget chain.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-36944
- https://github.com/scala/scala/pull/10118
- https://discuss.lightbend.com/t/impact-of-cve-2022-36944-on-akka-cluster-akka-actor-akka-remote/10007/2
- https://github.com/scala/scala
- https://github.com/scala/scala-collection-compat/releases/tag/v2.9.0
- https://github.com/scala/scala/releases/tag/v2.13.9
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/6ZOZVWY3X72FZZCCRAKRJYTQOJ6LUD6Z
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/L3WMKPFAMFQE3HJVRQ5KOJUTWG264SXI
- https://www.scala-lang.org/download
