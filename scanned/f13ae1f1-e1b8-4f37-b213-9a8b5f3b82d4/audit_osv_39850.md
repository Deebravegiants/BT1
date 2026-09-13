# [M] Unsafe Java deserialization in SerializingHttpMessageConverter — remote code execution

## Summary
Severity: Medium
Advisory: CVE-2026-47864
CVSS: 6.4 (CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:L/A:L)
Published: 2026-08-27
Source: https://osv.dev/vulnerability/CVE-2026-47864
Type: osv

## Details
SerializingHttpMessageConverter deserializes the body of incoming HTTP requests with a raw java.io.ObjectInputStream and no class filtering. Any request with Content-Type application/x-java-serialized-object whose body resolves to a Serializable type is read directly via readObject(). If an application using this converter on an inbound HTTP endpoint has any known Java deserialization "gadget" on its classpath, a remote, unauthenticated attacker can achieve arbitrary code execution.
Spring Integration 7.1.0
Spring Integration 7.0.0 - 7.0.5
Spring Integration 6.5.0 - 6.5.10
Spring Integration 6.4.0 - 6.4.12
Spring Integration 5.5.21 and earlier

## References
- https://spring.io/security/cve-2026-47864
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/47xxx/CVE-2026-47864.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-47864
