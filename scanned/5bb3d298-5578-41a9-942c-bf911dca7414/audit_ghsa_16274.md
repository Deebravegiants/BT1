# [M] Etcd Gateway TLS endpoint validation only confirms TCP reachability

## Summary
Severity: Medium
Advisory: GHSA-j86v-2vjr-fg8f
Ecosystem: Go
Published: 2024-02-03
Source: https://github.com/advisories/GHSA-j86v-2vjr-fg8f
Type: github-advisory

## Affected
- Go: `go.etcd.io/etcd/v3` — affected >=3.4.0-rc.0 <3.4.10
- Go: `go.etcd.io/etcd/v3` — affected >=0 <3.3.23

## Details
### Vulnerability type
Cryptography

### Workarounds
Refer to the [gateway documentation](https://github.com/etcd-io/etcd/blob/master/Documentation/op-guide/gateway.md). The vulnerability was spotted due to unclear documentation of how the gateway handles endpoints validation. 

### Detail
Secure endpoint validation is performed by the etcd gateway start command when the --discovery-srv flag is enabled. However, as currently implemented, it only validates TCP reachability, effectively allowing connections to an endpoint that doesn't accept TLS connections through the HTTPS URL. The auditors has noted that appropriate documentation of this validation functionality plus deprecation of this misleading functionality is an acceptable path forward.

### References
Find out more on this vulnerability in the [security audit report](https://github.com/etcd-io/etcd/blob/master/security/SECURITY_AUDIT.pdf)

### For more information
If you have any questions or comments about this advisory:
* Contact the [etcd security committee](https://github.com/etcd-io/etcd/blob/master/security/security-release-process.md#product-security-committee-psc)

## References
- https://github.com/etcd-io/etcd/security/advisories/GHSA-j86v-2vjr-fg8f
