# [H] Etcd Gateway can include itself as an endpoint resulting in resource exhaustion

## Summary
Severity: High
Advisory: GHSA-2xhq-gv6c-p224
CVE: CVE-2020-15114
CWE: CWE-400, CWE-772
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:N/I:N/A:H (CVSS_V3)
Published: 2024-01-31
Source: https://github.com/advisories/GHSA-2xhq-gv6c-p224
Type: github-advisory

## Affected
- Go: `go.etcd.io/etcd` — affected >=3.4.0-rc.0 <3.4.10
- Go: `go.etcd.io/etcd` — affected >=0 <3.3.23

## Details
### Vulnerability type
Denial of Service

### Detail
The etcd gateway is a simple TCP proxy to allow for basic service discovery and access. However, it is possible to include the gateway address as an endpoint. This results in a denial of service, since the endpoint can become stuck in a loop of requesting itself until there are no more available file descriptors to accept connections on the gateway.

### References
Find out more on this vulnerability in the [security audit report](https://github.com/etcd-io/etcd/blob/master/security/SECURITY_AUDIT.pdf)

### For more information
If you have any questions or comments about this advisory:
* Contact the [etcd security committee](https://github.com/etcd-io/etcd/blob/master/security/security-release-process.md#product-security-committee-psc)

## References
- https://github.com/etcd-io/etcd/security/advisories/GHSA-2xhq-gv6c-p224
- https://nvd.nist.gov/vuln/detail/CVE-2020-15114
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/L6B6R43Y7M3DCHWK3L3UVGE2K6WWECMP
