# [M] In Spring AMQP the link credit never replenished on listener exception path

## Summary
Severity: Medium
Advisory: CVE-2026-59320
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-08-27
Source: https://osv.dev/vulnerability/CVE-2026-59320
Type: osv

## Details
When a container-level ErrorHandler is configured (the mitigation for finding 221000), each delivery whose processing throws still permanently consumes one link credit. After initialCredits (default 100) failing messages the receiver's credit reaches zero and the broker stops delivering, leaving the listener silently stalled while isRunning() remains true.
Spring AMQP 4.1.0

## References
- https://spring.io/security/cve-2026-59320
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/59xxx/CVE-2026-59320.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-59320
