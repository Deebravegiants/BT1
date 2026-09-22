# [M] FlashMQ does not release memory of queued QoS messages

## Summary
Severity: Medium
Advisory: CVE-2025-62723
Aliases: GHSA-7mhp-22q4-r6vv
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:L)
Published: 2025-10-24
Source: https://osv.dev/vulnerability/CVE-2025-62723
Type: osv

## Details
FlashMQ is a MQTT broker/server, designed for multi-CPU environments. Prior to version 1.23.2, any authenticated user can create sessions and have them collect QoS messages. When not sent to a client, these are then not released upon (eventual) session expiration. Version 1.23.2 fixes the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/62xxx/CVE-2025-62723.json
- https://github.com/halfgaar/FlashMQ/security/advisories/GHSA-7mhp-22q4-r6vv
- https://nvd.nist.gov/vuln/detail/CVE-2025-62723
- https://github.com/halfgaar/FlashMQ/issues/154
- https://github.com/halfgaar/FlashMQ/commit/e86c49360ef4387440c97f591770cdb9284b4ee9
