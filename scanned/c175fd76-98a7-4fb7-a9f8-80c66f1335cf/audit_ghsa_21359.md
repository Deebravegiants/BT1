# [M] etcd's WAL `ReadAll`  method vulnerable to an entry with large index causing panic

## Summary
Severity: Medium
Advisory: GHSA-m332-53r6-2w93
CVE: CVE-2020-15112
CWE: CWE-129, CWE-20
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2022-10-06
Source: https://github.com/advisories/GHSA-m332-53r6-2w93
Type: github-advisory

## Affected
- Go: `go.etcd.io/etcd/v3` — affected >=0 <3.3.23
- Go: `go.etcd.io/etcd/v3` — affected >=3.4.0 <3.4.10

## Details
### Vulnerability type
Data Validation

### Detail
In the ReadAll method in wal/wal.go, it is possible to have an entry index greater then the number of entries. This could cause issues when WAL entries are being read during consensus as an arbitrary etcd consensus participant could go down from a runtime panic when reading the entry.

### References
Find out more on this vulnerability in the [security audit report](https://github.com/etcd-io/etcd/blob/master/security/SECURITY_AUDIT.pdf)

### For more information
If you have any questions or comments about this advisory:
* Contact the [etcd security committee](https://github.com/etcd-io/etcd/blob/master/security/security-release-process.md)

## References
- https://github.com/etcd-io/etcd/security/advisories/GHSA-m332-53r6-2w93
- https://nvd.nist.gov/vuln/detail/CVE-2020-15112
- https://github.com/etcd-io/etcd/pull/11793
- https://github.com/etcd-io/etcd/commit/7d1cf640497cbcdfb932e619b13624112c7e3865
- https://github.com/etcd-io/etcd/commit/f4b650b51dc4a53a8700700dc12e1242ac56ba07
- https://github.com/etcd-io/etcd
- https://github.com/etcd-io/etcd/blob/master/security/SECURITY_AUDIT.pdf
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/L6B6R43Y7M3DCHWK3L3UVGE2K6WWECMP
- https://pkg.go.dev/vuln/GO-2020-0005
