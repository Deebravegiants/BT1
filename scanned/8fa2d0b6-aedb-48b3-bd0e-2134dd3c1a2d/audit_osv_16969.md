# [H] CVE-2020-10996

## Summary
Severity: High
Advisory: CVE-2020-10996
CVSS: 8.1 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-04-27
Source: https://osv.dev/vulnerability/CVE-2020-10996
Type: osv

## Details
An issue was discovered in Percona XtraDB Cluster before 5.7.28-31.41.2. A bundled script inadvertently sets a static transition_key for SST processes in place of the random key expected.

## References
- https://www.percona.com/blog/2020/04/20/cve-2020-10996-percona-xtradb-cluster-sst-script-static-key/
- https://www.percona.com/doc/percona-xtradb-cluster/LATEST/release-notes/Percona-XtraDB-Cluster-5.7.28-31.41.2.html
- https://jira.percona.com/browse/PXC-3117
