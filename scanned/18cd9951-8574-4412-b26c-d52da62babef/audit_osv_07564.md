# [M] Improper access to dataset metadata information

## Summary
Severity: Medium
Advisory: BIT-superset-2021-37839
Aliases: CVE-2021-37839, GHSA-748r-5r8q-273m, PYSEC-2026-776
Ecosystem: Bitnami
Published: 2025-02-05
Source: https://osv.dev/vulnerability/BIT-superset-2021-37839
Type: osv

## Affected
- Bitnami: `superset` — affected >=0 <1.5.2

## Details
Apache Superset up to 1.5.1 allowed for authenticated users to access metadata information related to datasets they have no permission on. This metadata included the dataset name, columns and metrics.

## References
- https://lists.apache.org/thread/pwqyxxmn5gh7cnw3qsp66v0lt4xojt82
- https://nvd.nist.gov/vuln/detail/CVE-2021-37839
