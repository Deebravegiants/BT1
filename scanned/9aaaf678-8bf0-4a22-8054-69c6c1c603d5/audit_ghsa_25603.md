# [H] go.etcd.io/etcd Authentication Bypass

## Summary
Severity: High
Advisory: GHSA-h6xx-pmxh-3wgp
CVE: CVE-2018-16886
CWE: CWE-285, CWE-287
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-04-12
Source: https://github.com/advisories/GHSA-h6xx-pmxh-3wgp
Type: github-advisory

## Affected
- Go: `go.etcd.io/etcd/v3` — affected >=3.2.0 <3.2.26
- Go: `go.etcd.io/etcd/v3` — affected >=3.3.0 <3.3.11
- Go: `go.etcd.io/etcd` — affected >=0 <0.5.0-alpha.5.0.20190108173120-83c051b701d3

## Details
etcd versions 3.2.x before 3.2.26 and 3.3.x before 3.3.11 are vulnerable to an improper authentication issue when role-based access control (RBAC) is used and client-cert-auth is enabled. If an etcd client server TLS certificate contains a Common Name (CN) which matches a valid RBAC username, a remote attacker may authenticate as that user with any valid (trusted) client certificate in a REST API request to the gRPC-gateway.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-16886
- https://github.com/etcd-io/etcd/pull/10366
- https://github.com/etcd-io/etcd/commit/0191509637546621d6f2e18e074e955ab8ef374d
- https://github.com/etcd-io/etcd/commit/bf9d0d8291dc71ecbfb2690612954e1a298154b2
- https://access.redhat.com/errata/RHSA-2019:0237
- https://access.redhat.com/errata/RHSA-2019:1352
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2018-16886
- https://github.com/etcd-io/etcd
- https://github.com/etcd-io/etcd/blob/1eee465a43720d713bb69f7b7f5e120135fdb1ac/CHANGELOG-3.2.md#security-authentication
- https://github.com/etcd-io/etcd/blob/1eee465a43720d713bb69f7b7f5e120135fdb1ac/CHANGELOG-3.3.md#security-authentication
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/JX7QTIT465BQGRGNCE74RATRQLKT2QE4
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/UPGYHMSKDPW5GAMI7BEP3XQRVRLLBJKS
- https://pkg.go.dev/vuln/GO-2021-0077
- http://www.securityfocus.com/bid/106540
