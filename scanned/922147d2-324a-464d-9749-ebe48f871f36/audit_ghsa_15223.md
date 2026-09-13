# [M] Improper Preservation of Permissions in etcd

## Summary
Severity: Medium
Advisory: GHSA-chh6-ppwq-jh92
CVE: CVE-2020-15113
CWE: CWE-281
Ecosystem: Go
CVSS: CVSS:3.1/AV:L/AC:H/PR:H/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2024-01-30
Source: https://github.com/advisories/GHSA-chh6-ppwq-jh92
Type: github-advisory

## Affected
- Go: `github.com/etcd-io/etcd` — affected >=3.4.0-rc.0 <3.4.10
- Go: `github.com/etcd-io/etcd` — affected >=0 <3.3.23

## Details
### Vulnerability type
Access Controls

### Detail
etcd creates certain directory paths (etcd data directory and the directory path when provided to automatically generate self-signed certificates for TLS connections with clients) with restricted access permissions (700) by using the os.MkdirAll. This function does not perform any permission checks when a given directory path exists already.
### Specific Go Package Affected
github.com/etcd-io/etcd/pkg/fileutil
### Workarounds
Make sure these directories have the desired permit (700).

### References
Find out more on this vulnerability in the [security audit report](https://github.com/etcd-io/etcd/blob/master/security/SECURITY_AUDIT.pdf)

### For more information
If you have any questions or comments about this advisory:
* Contact the [etcd security committee](https://github.com/etcd-io/etcd/blob/master/security/security-release-process.md#product-security-committee-psc)

## References
- https://github.com/etcd-io/etcd/security/advisories/GHSA-chh6-ppwq-jh92
- https://nvd.nist.gov/vuln/detail/CVE-2020-15113
- https://github.com/etcd-io/etcd/commit/6be5c54c94298ae6746a574d2af8227d0c9a998b
- https://github.com/etcd-io/etcd/commit/e5424fc474b274c9e6b5205165015bc2035745f2
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/L6B6R43Y7M3DCHWK3L3UVGE2K6WWECMP
