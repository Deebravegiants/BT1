# [M] Lack of proper validation of server UUID can be used by the server to trick the client to accept invalid proofs

## Summary
Severity: Medium
Advisory: GHSA-6cqj-6969-p57x
CVE: CVE-2022-39199
CWE: CWE-345
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:H/UI:N/S:C/C:N/I:H/A:N (CVSS_V3)
Published: 2022-11-21
Source: https://github.com/advisories/GHSA-6cqj-6969-p57x
Type: github-advisory

## Affected
- Go: `github.com/codenotary/immudb` — affected >=0 <1.4.1

## Details
### Impact

immudb client SDKs use server's UUID to distinguish between different server instance so that the client can connect to different immudb instances and keep the state for multiple servers. SDK does not validate this uuid and can accept any value reported by the server. A malicious server can change the reported UUID tricking the client to treat it as a different server thus accepting a state completely irrelevant to the one previously retrieved from the server.

### Patches

The following Go SDK versions are not vulnerable:

| **SDK** | **Version** |
|-------|------------|
| [go](pkg.go.dev/github.com/codenotary/immudb/pkg/client) | 1.4.1 |

### Workarounds

When initializing an immudb client object, a custom state handler can be used to store the state. Providing custom implementation that ignores the server UUID can be used to ensure that even if the server changes the UUID, client will still consider it to be the same server.

### For more information

If you have any questions or comments about this advisory:

* Open a discussion in [immudb Discussions](https://github.com/codenotary/immudb/discussions/new)
* Email us at [immudb-security@codenotary.com](mailto:immudb-security@codenotary.com)

## References
- https://github.com/codenotary/immudb/security/advisories/GHSA-6cqj-6969-p57x
- https://nvd.nist.gov/vuln/detail/CVE-2022-39199
- https://github.com/codenotary/immudb/commit/cade04756ff3f0a3b9e8d24149062744574adf5d
- https://github.com/codenotary/immudb
- https://github.com/codenotary/immudb/releases/tag/v1.4.1
- https://pkg.go.dev/vuln/GO-2022-1118
