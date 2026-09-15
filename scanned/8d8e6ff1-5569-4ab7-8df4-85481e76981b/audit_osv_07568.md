# [M] Apache Superset: Incorrect default permissions for Gamma role

## Summary
Severity: Medium
Advisory: BIT-superset-2023-27525
Aliases: CVE-2023-27525, GHSA-7jhg-8m74-6f6g, PYSEC-2026-1163
Ecosystem: Bitnami
Published: 2025-02-05
Source: https://osv.dev/vulnerability/BIT-superset-2023-27525
Type: osv

## Affected
- Bitnami: `superset` — affected >=0 <2.0.2

## Details
An authenticated user with Gamma role authorization could have access to metadata information using non trivial methods in Apache Superset up to and including 2.0.1

## References
- https://lists.apache.org/thread/wpv7b17zjg2pmvpfkdd6nn8sco8y2q77
- https://nvd.nist.gov/vuln/detail/CVE-2023-27525
