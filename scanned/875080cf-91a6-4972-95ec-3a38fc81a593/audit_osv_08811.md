# [M] CVE-2016-6225

## Summary
Severity: Medium
Advisory: CVE-2016-6225
CVSS: 5.9 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2017-03-23
Source: https://osv.dev/vulnerability/CVE-2016-6225
Type: osv

## Details
xbcrypt in Percona XtraBackup before 2.3.6 and 2.4.x before 2.4.5 does not properly set the initialization vector (IV) for encryption, which makes it easier for context-dependent attackers to obtain sensitive information from encrypted backup files via a Chosen-Plaintext attack. NOTE: this vulnerability exists because of an incomplete fix for CVE-2013-6394.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/BAHI6ETS22FJCMLW7A6SICFKQXF5G2VI/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/ZBVCP6KLFVGG6HSGLHLTMZRD6C4IJSZP/
- http://lists.opensuse.org/opensuse-updates/2017-01/msg00125.html
- http://lists.opensuse.org/opensuse-updates/2017-01/msg00126.html
- https://www.percona.com/blog/2017/01/12/cve-2016-6225-percona-xtrabackup-encryption-iv-not-set-properly/
- https://bugs.launchpad.net/percona-xtrabackup/+bug/1643949
- https://github.com/percona/percona-xtrabackup/pull/266
- https://github.com/percona/percona-xtrabackup/pull/267
