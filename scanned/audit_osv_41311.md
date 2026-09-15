# [M] Remote JVM termination: nested-array Java deserialization bypasses allowlist, triggers StackOverflowError, default JavaLangErrorHandler calls System.exit(99)

## Summary
Severity: Medium
Advisory: CVE-2026-59275
CVSS: 6.6 (CVSS:3.1/AV:N/AC:H/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-27
Source: https://osv.dev/vulnerability/CVE-2026-59275
Type: osv

## Details
A single hostile AMQP message can terminate the entire consumer JVM (System.exit(99)), not just the listener thread — full availability loss for every workload co-located in that process.
Spring AMQP 4.1.0
Spring AMQP 4.0.0 - 4.0.4
Spring AMQP 3.2.0 - 3.2.12
Spring AMQP 2.4.18 and earlier

## References
- https://spring.io/security/cve-2026-59275
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/59xxx/CVE-2026-59275.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-59275
