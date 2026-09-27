# [M] Improper Input Validation in Kibana Email Connector Leading to Excessive Allocation

## Summary
Severity: Medium
Advisory: BIT-elk-2026-0543
Aliases: BIT-kibana-2026-0543, CVE-2026-0543
Ecosystem: Bitnami
Published: 2026-01-16
Source: https://osv.dev/vulnerability/BIT-elk-2026-0543
Type: osv

## Affected
- Bitnami: `elk` — affected >=9.2.0 <9.2.4

## Details
Improper Input Validation (CWE-20) in Kibana's Email Connector can allow an attacker to cause an Excessive Allocation (CAPEC-130) through a specially crafted email address parameter. This requires an attacker to have authenticated access with view-level privileges sufficient to execute connector actions. The application attempts to process specially crafted email format, resulting in complete service unavailability for all users until manual restart is performed.

## References
- https://discuss.elastic.co/t/kibana-8-19-10-9-1-10-9-2-4-security-update-esa-2026-08/384523
- https://nvd.nist.gov/vuln/detail/CVE-2026-0543
