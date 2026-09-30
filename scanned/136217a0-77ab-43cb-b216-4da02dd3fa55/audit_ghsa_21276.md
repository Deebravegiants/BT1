# [M] etcd has no minimum password length

## Summary
Severity: Medium
Advisory: GHSA-4993-m7g5-r9hh
CVE: CVE-2020-15115
CWE: CWE-521
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:L/I:N/A:N (CVSS_V3)
Published: 2022-10-06
Source: https://github.com/advisories/GHSA-4993-m7g5-r9hh
Type: github-advisory

## Affected
- Go: `go.etcd.io/etcd/client/v3` — affected >=3.4.0 <3.4.10
- Go: `go.etcd.io/etcd/client/v3` — affected >=0 <3.3.23

## Details
### Vulnerability type
Access Control

### Workarounds
The etcdctl and etcd API do not enforce a specific password length during user creation or user password update operations. [It is the responsibility of the administrator to enforce these requirements](https://github.com/etcd-io/etcd/blob/master/Documentation/op-guide/authentication.md#notes-on-password-strength).

### Detail
etcd does not perform any password length validation, which allows for very short passwords, such as those with a length of one. This may allow an attacker to guess or brute-force users’ passwords with little computational effort.

### References
Find out more on this vulnerability in the [security audit report](https://github.com/etcd-io/etcd/blob/master/security/SECURITY_AUDIT.pdf)

### For more information
If you have any questions or comments about this advisory:
* Contact the [etcd security committee](https://github.com/etcd-io/etcd/blob/master/security/security-release-process.md#product-security-committee-psc)

## References
- https://github.com/etcd-io/etcd/security/advisories/GHSA-4993-m7g5-r9hh
- https://nvd.nist.gov/vuln/detail/CVE-2020-15115
- https://github.com/etcd-io/etcd
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/L6B6R43Y7M3DCHWK3L3UVGE2K6WWECMP
