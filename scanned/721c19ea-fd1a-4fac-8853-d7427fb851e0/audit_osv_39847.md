# [M] Unbounded decompression of attacker-supplied compressed message bodies

## Summary
Severity: Medium
Advisory: CVE-2026-47860
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-08-26
Source: https://osv.dev/vulnerability/CVE-2026-47860
Type: osv

## Details
An attacker who can publish to a queue consumed by an application that has enabled message decompression can crash the consumer JVM with a single ~1 MB message.
Spring AMQP 4.1.0
Spring AMQP 4.0.0 - 4.0.4
Spring AMQP 3.2.0 - 3.2.12
Spring AMQP 2.4.18 and earlier

## References
- https://spring.io/security/cve-2026-47860
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/47xxx/CVE-2026-47860.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-47860
