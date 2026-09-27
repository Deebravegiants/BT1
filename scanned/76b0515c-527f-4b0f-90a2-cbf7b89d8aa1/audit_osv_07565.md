# [M] Apache Superset: Improper rendering of user input

## Summary
Severity: Medium
Advisory: BIT-superset-2022-43720
Aliases: CVE-2022-43720, GHSA-fpmr-qmgh-42x2, PYSEC-2026-782
Ecosystem: Bitnami
Published: 2025-02-05
Source: https://osv.dev/vulnerability/BIT-superset-2022-43720
Type: osv

## Affected
- Bitnami: `superset` — affected >=2.0.0 <2.0.1

## Details
An authenticated attacker with write CSS template permissions can create a record with specific HTML tags that will not get properly escaped by the toast message displayed when a user deletes that specific CSS template record. This issue affects Apache Superset version 1.5.2 and prior versions and version 2.0.0.

## References
- https://lists.apache.org/thread/jts6x56kghr9mbowb653bk70pl81jp8l
- https://nvd.nist.gov/vuln/detail/CVE-2022-43720
