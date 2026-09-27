# [M] CVE-2022-45866

## Summary
Severity: Medium
Advisory: CVE-2022-45866
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2022-11-23
Source: https://osv.dev/vulnerability/CVE-2022-45866
Type: osv

## Details
qpress before PierreLvx/qpress 20220819 and before version 11.3, as used in Percona XtraBackup and other products, allows directory traversal via ../ in a .qp file.

## References
- https://github.com/PierreLvx/qpress/compare/20170415...20220819
- https://pkgs.org/download/qpress
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/45xxx/CVE-2022-45866.json
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/BQWF7635AJSDKEIGLB73XAH643POGTFY/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/G4RXO3VYIFRTNIFHWIAZWND6ZXQ5OYOB/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/UUZ73XT2FXLHC7I4ODLOVB4O4QN7Q7JB/
- https://nvd.nist.gov/vuln/detail/CVE-2022-45866
- https://github.com/EvgeniyPatlan/qpress/commit/ddb312090ebd5794e81bc6fb1dfb4e79eda48761
- https://github.com/PierreLvx/qpress/pull/6
- https://github.com/percona/percona-xtrabackup/pull/1366
