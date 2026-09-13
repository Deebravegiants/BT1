# [C] Deserialization of Untrusted Data in Apache jUDDI

## Summary
Severity: Critical
Advisory: GHSA-9hx8-2mrv-r674
CVE: CVE-2021-37578
CWE: CWE-502
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-08-09
Source: https://github.com/advisories/GHSA-9hx8-2mrv-r674
Type: github-advisory

## Affected
- Maven: `org.apache.juddi:juddi-core` — affected >=0 <3.3.10

## Details
Apache jUDDI uses several classes related to Java's Remote Method Invocation (RMI) which (as an extension to UDDI) provides an alternate transport for accessing UDDI services.

RMI uses the default Java serialization mechanism to pass parameters in RMI invocations. A remote attacker can send a malicious serialized object to the above RMI entries. The objects get deserialized without any check on the incoming data. In the worst case, it may let the attacker run arbitrary code remotely. 

For both jUDDI web service applications and jUDDI clients, the usage of RMI is disabled by default. Since this is an optional feature and an extension to the UDDI protocol, the likelihood of impact is low. Starting with 3.3.10, all RMI related code was removed.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-37578
- https://github.com/apache/juddi/commit/dd880ffe7694a70cee75efeee79c9197d261866f
- https://github.com/apache/juddi
- https://lists.apache.org/thread.html/r82047b3ba774cf870ea8e1e9ec51c6107f6cd056d4e36608148c6e71%40%3Cprivate.juddi.apache.org%3E
- http://www.openwall.com/lists/oss-security/2021/07/29/1
