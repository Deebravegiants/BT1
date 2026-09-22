# [M] Shared JSR-223 ScriptEngine evaluated concurrently without THREADING check

## Summary
Severity: Medium
Advisory: CVE-2026-59321
CVSS: 4.2 (CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:L/I:L/A:N)
Published: 2026-08-27
Source: https://osv.dev/vulnerability/CVE-2026-59321
Type: osv

## Details
A single ScriptEngine instance is reused for every message on a script-backed channel. For JSR-223 engines that report THREADING=null (not thread-safe, e.g. the Kotlin kts engine), concurrent message processing can corrupt engine-internal state, potentially leaking one message's payload/headers bindings into another message's script evaluation or throwing spurious exceptions.
Spring Integration 7.1.0
Spring Integration 7.0.0 - 7.0.5
Spring Integration 6.5.0 - 6.5.10
Spring Integration 6.4.0 - 6.4.12
Spring Integration 5.5.21 and earlier

## References
- https://spring.io/security/cve-2026-59321
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/59xxx/CVE-2026-59321.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-59321
