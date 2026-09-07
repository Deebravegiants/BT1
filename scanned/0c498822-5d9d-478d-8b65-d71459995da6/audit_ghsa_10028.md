# [H] Apache Storm: Deserialization of Untrusted Data vulnerability

## Summary
Severity: High
Advisory: GHSA-jf89-3q6q-vcgr
CVE: CVE-2026-35337
CWE: CWE-502
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-04-13
Source: https://github.com/advisories/GHSA-jf89-3q6q-vcgr
Type: github-advisory

## Affected
- Maven: `org.apache.storm:storm-client` — affected >=0 <2.8.6

## Details
Deserialization of Untrusted Data vulnerability in Apache Storm.

Versions Affected:
before 2.8.6.


Description:
When processing topology credentials submitted via the Nimbus Thrift API, Storm deserializes the base64-encoded TGT blob using ObjectInputStream.readObject() without any class filtering or validation. An authenticated user with topology submission rights could supply a crafted serialized object in the "TGT" credential field, leading to remote code execution in both the Nimbus and Worker JVMs.


Mitigation:
2.x users should upgrade to 2.8.6.


Users who cannot upgrade immediately should monkey-patch an ObjectInputFilter allow-list to ClientAuthUtils.deserializeKerberosTicket() restricting deserialized classes to javax.security.auth.kerberos.KerberosTicket and its known dependencies. A guide on how to do this is available in the release notes of 2.8.6.

Credit: This issue was discovered by K.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-35337
- https://github.com/apache/storm
- https://storm.apache.org/2026/04/12/storm286-released.html
- http://www.openwall.com/lists/oss-security/2026/04/12/6
