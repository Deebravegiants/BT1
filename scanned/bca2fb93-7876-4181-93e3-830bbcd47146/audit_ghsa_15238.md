# [M] Etcd Gateway TLS authentication only applies to endpoints detected in DNS SRV records

## Summary
Severity: Medium
Advisory: GHSA-wr2v-9rpq-c35q
CVE: CVE-2020-15136
CWE: CWE-287, CWE-306
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2024-01-31
Source: https://github.com/advisories/GHSA-wr2v-9rpq-c35q
Type: github-advisory

## Affected
- Go: `go.etcd.io/etcd` — affected >=3.4.0-rc.0 <3.4.10
- Go: `go.etcd.io/etcd` — affected >=0 <3.3.23

## Details
### Vulnerability type
Cryptography

### Workarounds
Refer to the [gateway documentation](https://github.com/etcd-io/etcd/blob/master/Documentation/op-guide/gateway.md). The vulnerability was spotted due to unclear documentation of how the gateway handles endpoints validation.

### Detail
When starting a gateway, TLS authentication will only be attempted on endpoints identified in DNS SRV records for a given domain, which occurs in the discoverEndpoints function. No authentication is performed against endpoints provided in the --endpoints flag. The auditors has noted that appropriate documentation of this validation functionality plus deprecation of this misleading functionality is an acceptable path forward.
 
### References
Find out more on this vulnerability in the [security audit report](https://github.com/etcd-io/etcd/blob/master/security/SECURITY_AUDIT.pdf)

### For more information
If you have any questions or comments about this advisory:
* Contact the [etcd security committee](https://github.com/etcd-io/etcd/blob/master/security/security-release-process.md#product-security-committee-psc)

## References
- https://github.com/etcd-io/etcd/security/advisories/GHSA-wr2v-9rpq-c35q
- https://nvd.nist.gov/vuln/detail/CVE-2020-15136
- https://github.com/etcd-io/etcd/blob/master/Documentation/op-guide/gateway.md
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/L6B6R43Y7M3DCHWK3L3UVGE2K6WWECMP
