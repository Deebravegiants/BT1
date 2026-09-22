# [H] Camel-MINA Vulnerable to Deserialization of Untrusted Data

## Summary
Severity: High
Advisory: GHSA-vpr3-2659-rw55
CVE: CVE-2026-40473
CWE: CWE-502
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-04-27
Source: https://github.com/advisories/GHSA-vpr3-2659-rw55
Type: github-advisory

## Affected
- Maven: `org.apache.camel:camel-mina` — affected >=3.0.0 <4.14.6
- Maven: `org.apache.camel:camel-mina` — affected >=4.15.0 <4.18.2
- Maven: `org.apache.camel:camel-mina` — affected >=4.19.0 <4.20.0

## Details
The camel-mina component's MinaConverter.toObjectInput(IoBuffer) type converter wraps an IoBuffer in a java.io.ObjectInputStream without applying any ObjectInputFilter or class-loading restrictions. When a Camel route uses camel-mina as a TCP or UDP consumer and requests conversion to ObjectInput (for example via getBody(ObjectInput.class) or @Body ObjectInput), an attacker sending a crafted serialized Java object over the network to the MINA consumer port can trigger arbitrary code execution in the context of the application during readObject().

This issue affects Apache Camel: from 3.0.0 before 4.14.6, from 4.15.0 before 4.18.2, from 4.19.0 before 4.20.0.

Users are recommended to upgrade to version 4.20.0, which fixes the issue. If users are on the 4.14.x LTS releases stream, then they are suggested to upgrade to 4.14.6. If users are on the 4.18.x releases stream, then they are suggested to upgrade to 4.18.2.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-40473
- https://github.com/apache/camel/pull/22583
- https://github.com/apache/camel/pull/22584
- https://github.com/apache/camel/pull/22585
- https://github.com/apache/camel/commit/8e7f6335d2b4b096df26f8221723405ceaee275a
- https://github.com/apache/camel/commit/b605816d11c253d22989abc290c198be83e3f817
- https://github.com/apache/camel/commit/c35b0a3720f8c80025b06112d5d9c2932426d7f0
- https://camel.apache.org/security/CVE-2026-40473.html
- https://github.com/apache/camel
- https://issues.apache.org/jira/browse/CAMEL-23319
- http://www.openwall.com/lists/oss-security/2026/04/26/8
