# [M] BIT-haproxy-2023-0056

## Summary
Severity: Medium
Advisory: BIT-haproxy-2023-0056
Aliases: CVE-2023-0056
Ecosystem: Bitnami
Published: 2024-01-31
Source: https://osv.dev/vulnerability/BIT-haproxy-2023-0056
Type: osv

## Affected
- Bitnami: `haproxy` — affected unspecified

## Details
An uncontrolled resource consumption vulnerability was discovered in HAProxy which could crash the service. This issue could allow an authenticated remote attacker to run a specially crafted malicious server in an OpenShift cluster. The biggest impact is to availability.

## References
- https://access.redhat.com/security/cve/CVE-2023-0056
