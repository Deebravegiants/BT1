# [H] Apache Thrift: Specially crafted input can crash a c_glib Thrift server with invalid pointer error.

## Summary
Severity: High
Advisory: BIT-thrift-2025-48431
Aliases: CVE-2025-48431
Ecosystem: Bitnami
Published: 2026-04-29
Source: https://osv.dev/vulnerability/BIT-thrift-2025-48431
Type: osv

## Affected
- Bitnami: `thrift` — affected >=0 <0.23.0

## Details
Mismatched Memory Management Routines vulnerability in Apache Thrift c_glib language bindings.

This issue affects Apache Thrift: before 0.23.0.

Users are recommended to upgrade to version 0.23.0, which fixes the issue.

Description: Specially crafted requests can crash an c_glib-based Thrift server with a clean but fatal "free(): invalid pointer" error message.

## References
- http://www.openwall.com/lists/oss-security/2026/04/28/8
- https://lists.apache.org/thread/lb4j0zyd5f3g36cos0wql925przpnwql
- https://nvd.nist.gov/vuln/detail/CVE-2025-48431
- https://access.redhat.com/errata/RHSA-2026:24539
- https://access.redhat.com/errata/RHSA-2026:25273
- https://access.redhat.com/errata/RHSA-2026:27126
- https://access.redhat.com/errata/RHSA-2026:28010
- https://access.redhat.com/security/cve/CVE-2025-48431
- https://bugzilla.redhat.com/show_bug.cgi?id=2463410
- https://security.access.redhat.com/data/csaf/v2/vex/2025/cve-2025-48431.json
- https://access.redhat.com/errata/RHSA-2026:36882
