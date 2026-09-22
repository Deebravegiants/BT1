# [M] BIT-percona-xtrabackup-2022-26944

## Summary
Severity: Medium
Advisory: BIT-percona-xtrabackup-2022-26944
Aliases: BIT-percona-xtrabackup-binary-2022-26944, CVE-2022-26944
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-percona-xtrabackup-2022-26944
Type: osv

## Affected
- Bitnami: `percona-xtrabackup` — affected >=2.4.20

## Details
Percona XtraBackup 2.4.20 unintentionally writes the command line to any resulting backup file output. This may include sensitive arguments passed at run time. In addition, when --history is passed at run time, this command line is also written to the PERCONA_SCHEMA.xtrabackup_history table. NOTE: this issue exists because of an incomplete fix for CVE-2020-10997.

## References
- https://docs.percona.com/percona-xtrabackup/2.4/release-notes/2.4/2.4.25.html
- https://jira.percona.com/browse/PXB-2722
