# [M] golang.org/x/sys/unix has Incorrect privilege reporting in syscall

## Summary
Severity: Medium
Advisory: GHSA-p782-xgp4-8hr8
CVE: CVE-2022-29526
CWE: CWE-269
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-06-24
Source: https://github.com/advisories/GHSA-p782-xgp4-8hr8
Type: github-advisory

## Affected
- Go: `golang.org/x/sys` — affected >=0 <0.0.0-20220412211240-33da011f77ad

## Details
Go before 1.17.10 and 1.18.x before 1.18.2 has Incorrect Privilege Reporting in syscall. When called with a non-zero flags parameter, the Faccessat function could incorrectly report that a file is accessible.

### Specific Go Packages Affected
golang.org/x/sys/unix

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-29526
- https://github.com/golang/go/issues/52313
- https://github.com/golang/go
- https://go.dev/cl/399539
- https://go.dev/cl/400074
- https://go.dev/issue/52313
- https://groups.google.com/g/golang-announce
- https://groups.google.com/g/golang-announce/c/Y5qrqw_lWdU
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/Q6GE5EQGE4L2KRVGW4T75QVIYAXCLO5X
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/RQXU752ALW53OJAF5MG3WMR5CCZVLWW6
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/Z55VUVGO7E5PJFXIOVAY373NZRHBNCI5
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/ZY2SLWOQR4ZURQ7UBRZ7JIX6H6F5JHJR
- https://pkg.go.dev/vuln/GO-2022-0493
- https://security.gentoo.org/glsa/202208-02
- https://security.netapp.com/advisory/ntap-20220729-0001
