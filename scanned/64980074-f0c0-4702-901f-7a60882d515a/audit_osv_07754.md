# [H] BIT-unixodbc-2024-1013

## Summary
Severity: High
Advisory: BIT-unixodbc-2024-1013
Aliases: CVE-2024-1013
Ecosystem: Bitnami
Published: 2025-03-25
Source: https://osv.dev/vulnerability/BIT-unixodbc-2024-1013
Type: osv

## Affected
- Bitnami: `unixodbc` — affected unspecified

## Details
An out-of-bounds stack write flaw was found in unixODBC on 64-bit architectures where the caller has 4 bytes and callee writes 8 bytes. This issue may go unnoticed on little-endian architectures, while big-endian architectures can be broken.

## References
- https://access.redhat.com/security/cve/CVE-2024-1013
- https://bugzilla.redhat.com/show_bug.cgi?id=2260823
- https://github.com/lurcher/unixODBC/pull/157
