# [H] BIT-dremio-2024-23768

## Summary
Severity: High
Advisory: BIT-dremio-2024-23768
Aliases: CVE-2024-23768
Ecosystem: Bitnami
Published: 2024-07-01
Source: https://osv.dev/vulnerability/BIT-dremio-2024-23768
Type: osv

## Affected
- Bitnami: `dremio` — affected >=24.0.0 <24.3.1

## Details
Dremio before 24.3.1 allows path traversal. An authenticated user who has no privileges on certain folders (and the files and datasets in these folders) can access these folders, files, and datasets. To be successful, the user must have access to the source and at least one folder in the source. Affected versions are: 24.0.0 through 24.3.0, 23.0.0 through 23.2.3, and 22.0.0 through 22.2.2. Fixed versions are: 24.3.1 and later, 23.2.4 and later, and 22.2.3 and later.

## References
- https://docs.dremio.com/current/reference/bulletins/2024-01-12-01
