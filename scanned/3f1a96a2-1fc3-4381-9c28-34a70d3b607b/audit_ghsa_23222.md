# [H] Deserialization of Untrusted Data in Spring-flex

## Summary
Severity: High
Advisory: GHSA-8v4h-j42h-wfhc
CVE: CVE-2017-3203
CWE: CWE-502
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-8v4h-j42h-wfhc
Type: github-advisory

## Affected
- Maven: `org.springframework.flex:spring-flex` — affected >=0

## Details
The Java implementations of AMF3 deserializers in Pivotal/Spring Spring-flex derive class instances from java.io.Externalizable rather than the AMF3 specification's recommendation of flash.utils.IExternalizable. A remote attacker with the ability to spoof or control an RMI server connection may be able to send serialized Java objects that execute arbitrary code when deserialized.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-3203
- https://codewhitesec.blogspot.com/2017/04/amf.html
- https://www.kb.cert.org/vuls/id/307983
- http://www.securityweek.com/flaws-java-amf-libraries-allow-remote-code-execution
