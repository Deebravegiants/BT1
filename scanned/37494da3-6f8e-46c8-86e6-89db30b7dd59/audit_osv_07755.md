# [H] Valkey Affected by RESP Protocol Injection via Lua error_reply

## Summary
Severity: High
Advisory: BIT-valkey-2025-67733
Aliases: CVE-2025-67733, GHSA-p876-p7q5-hv2m
Ecosystem: Bitnami
Published: 2026-02-26
Source: https://osv.dev/vulnerability/BIT-valkey-2025-67733
Type: osv

## Affected
- Bitnami: `valkey` — affected >=9.0.0 <9.0.2

## Details
Valkey is a distributed key-value database. Prior to versions 9.0.2, 8.1.6, 8.0.7, and 7.2.12, a malicious user can use scripting commands to inject arbitrary information into the response stream for the given client, potentially corrupting or returning tampered data to other users on the same connection. The error handling code for lua scripts does not properly handle null characters. Versions 9.0.2, 8.1.6, 8.0.7, and 7.2.12 fix the issue.

## References
- https://github.com/valkey-io/valkey/security/advisories/GHSA-p876-p7q5-hv2m
- https://nvd.nist.gov/vuln/detail/CVE-2025-67733
- https://access.redhat.com/errata/RHSA-2026:3443
- https://access.redhat.com/errata/RHSA-2026:3507
- https://access.redhat.com/errata/RHSA-2026:5445
- https://access.redhat.com/security/cve/CVE-2025-67733
- https://bugzilla.redhat.com/show_bug.cgi?id=2442025
- https://security.access.redhat.com/data/csaf/v2/vex/2025/cve-2025-67733.json
