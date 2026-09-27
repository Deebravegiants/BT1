# [H] BIT-percona-xtrabackup-2022-25834

## Summary
Severity: High
Advisory: BIT-percona-xtrabackup-2022-25834
Aliases: BIT-percona-xtrabackup-binary-2022-25834, CVE-2022-25834
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-percona-xtrabackup-2022-25834
Type: osv

## Affected
- Bitnami: `percona-xtrabackup` — affected >=3.0.0 <8.0.27-19

## Details
In Percona XtraBackup (PXB) through 2.2.24 and 3.x through 8.0.27-19, a crafted filename on the local file system could trigger unexpected command shell execution of arbitrary commands.

## References
- https://docs.percona.com/percona-xtrabackup/8.0/release-notes/8.0/8.0.32-26.0.html#improvements
- https://www.percona.com/doc/percona-xtrabackup/2.4/index.html
