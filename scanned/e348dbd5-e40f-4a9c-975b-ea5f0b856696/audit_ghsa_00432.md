# [C] Deserialization of Untrusted Data in Pippo

## Summary
Severity: Critical
Advisory: GHSA-7fm6-2qw4-g3x3
CVE: CVE-2018-18628
CWE: CWE-502
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2018-10-24
Source: https://github.com/advisories/GHSA-7fm6-2qw4-g3x3
Type: github-advisory

## Affected
- Maven: `ro.pippo:pippo-core` — affected >=0 <1.12.0

## Details
An issue was discovered in Pippo 1.11.0. The function SerializationSessionDataTranscoder.decode() calls ObjectInputStream.readObject() to deserialize a SessionData object without checking the object types. An attacker can create a malicious object, base64 encode it, and place it in the PIPPO_SESSION field of a cookie. Sending this cookie may lead to remote code execution.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-18628
- https://github.com/pippo-java/pippo/issues/458
- https://github.com/pippo-java/pippo/commit/a82347d9d3358e98c89b48579d4285d807a57cc0
- https://github.com/pippo-java/pippo/commit/c6b26551a82d2dd32097fcb17c13c3b830916296
- https://github.com/advisories/GHSA-7fm6-2qw4-g3x3
- https://github.com/pippo-java/pippo
