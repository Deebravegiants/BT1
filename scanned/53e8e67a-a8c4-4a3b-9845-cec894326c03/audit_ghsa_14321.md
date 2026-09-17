# [M] vitess allows users to create keyspaces that can deny access to already existing keyspaces

## Summary
Severity: Medium
Advisory: GHSA-735r-hv67-g38f
CVE: CVE-2023-29194
CWE: CWE-20, CWE-703
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:N/I:N/A:L (CVSS_V3)
Published: 2023-04-11
Source: https://github.com/advisories/GHSA-735r-hv67-g38f
Type: github-advisory

## Affected
- Go: `vitess.io/vitess` — affected >=0 <0.16.1

## Details
### Impact
Users can either intentionally or inadvertently create a keyspace containing `/` characters such that from that point on, anyone who tries to view keyspaces from VTAdmin will receive an error. Trying to list all the keyspaces using `vtctldclient GetKeyspaces` will also return an error.
Note that all other keyspaces can still be administered using the CLI (vtctldclient).

### Patches
v16.0.1 (corresponding to 0.16.1 on pkg.go.dev)

### Workarounds
Delete the offending keyspace using a CLI client (vtctldclient) 
```
vtctldclient --server ... DeleteKeyspace a/b
```

Found during a security audit sponsored by the [CNCF](https://cncf.io) and facilitated by [OSTIF](https://ostif.org).

## References
- https://github.com/vitessio/vitess/security/advisories/GHSA-735r-hv67-g38f
- https://nvd.nist.gov/vuln/detail/CVE-2023-29194
- https://github.com/vitessio/vitess/commit/adf10196760ad0b3991a7aa7a8580a544e6ddf88
- https://github.com/vitessio/vitess
- https://github.com/vitessio/vitess/commits/v0.16.1
