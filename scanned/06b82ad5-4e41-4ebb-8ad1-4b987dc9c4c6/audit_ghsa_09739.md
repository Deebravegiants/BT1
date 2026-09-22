# [H] Camel-PQC Vulnerable to Deserialization of Untrusted Data

## Summary
Severity: High
Advisory: GHSA-v3vg-332r-mw99
CVE: CVE-2026-40048
CWE: CWE-502
Ecosystem: Maven
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-04-27
Source: https://github.com/advisories/GHSA-v3vg-332r-mw99
Type: github-advisory

## Affected
- Maven: `org.apache.camel:camel-pqc` — affected >=0 <4.18.2

## Details
The Camel-PQC FileBasedKeyLifecycleManager class deserializes the contents of `<keyId>.key` files in the configured key directory using java.io.ObjectInputStream without applying any ObjectInputFilter or class-loading restrictions. The cast to `java.security.KeyPair` is evaluated only after `readObject()` has already returned, so any `readObject()` side effects in the deserialized object run before the type check. An attacker who can write to the key directory used by a Camel application — for example through a path traversal into the directory, misconfigured filesystem permissions on the volume where keys are stored, a compromised key provisioning pipeline, or a symlink attack — can place a crafted serialized Java object that, when deserialized during normal key lifecycle operations, results in arbitrary code execution in the context of the application.

This issue affects Apache Camel: from 4.19.0 before 4.20.0, from 4.18.0 before 4.18.2.

Users are recommended to upgrade to version 4.20.0, which fixes the issue by replacing java.io.ObjectInputStream-based key and metadata storage with standard PKCS#8 (private key) / X.509 SubjectPublicKeyInfo (public key) Base64 JSON encoding. For users on the 4.18.x LTS releases stream, upgrade to 4.18.2.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-40048
- https://github.com/apache/camel/pull/22034
- https://github.com/apache/camel/pull/22495
- https://github.com/apache/camel/commit/5bdd0f1d3289dfa78116deec6c81083708bf432d
- https://github.com/apache/camel/commit/5f87a86f4e337efc59248d278c6a5650e73b3b7c
- https://camel.apache.org/security/CVE-2026-40048.html
- https://github.com/apache/camel
- https://issues.apache.org/jira/browse/CAMEL-23200
- http://www.openwall.com/lists/oss-security/2026/04/26/6
