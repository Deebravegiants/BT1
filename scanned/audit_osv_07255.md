# [M] BIT-percona-xtrabackup-2020-10997

## Summary
Severity: Medium
Advisory: BIT-percona-xtrabackup-2020-10997
Aliases: BIT-percona-xtrabackup-binary-2020-10997, CVE-2020-10997
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-percona-xtrabackup-2020-10997
Type: osv

## Affected
- Bitnami: `percona-xtrabackup` — affected >=8.0.4 <8.0.11

## Details
Percona XtraBackup before 2.4.20 unintentionally writes the command line to any resulting backup file output. This may include sensitive arguments passed at run time. In addition, when --history is passed at run time, this command line is also written to the PERCONA_SCHEMA.xtrabackup_history table.

## References
- https://jira.percona.com/browse/PXB-2142
- https://www.percona.com/blog/2020/04/16/cve-2020-10997-percona-xtrabackup-information-disclosure-of-command-line-arguments/
