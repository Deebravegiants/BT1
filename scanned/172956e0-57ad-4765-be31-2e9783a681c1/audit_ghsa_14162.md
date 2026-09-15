# [M] VTAdmin users that can create shards can deny access to other functions

## Summary
Severity: Medium
Advisory: GHSA-pqj7-jx24-wj7w
CVE: CVE-2023-29195
CWE: CWE-20, CWE-703
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:N/I:N/A:L (CVSS_V3)
Published: 2023-05-11
Source: https://github.com/advisories/GHSA-pqj7-jx24-wj7w
Type: github-advisory

## Affected
- Go: `vitess.io/vitess` — affected >=0 <0.16.2

## Details
### Impact
Users can either intentionally or inadvertently create a shard containing `/` characters from VTAdmin such that from that point on, anyone who tries to create a new shard from VTAdmin will receive an error. 
Attempting to view the keyspace(s) will also no longer work.
Creating a shard using `vtctldclient` does not have the same problem because the CLI validates the input correctly.

### Patches
v16.0.2, corresponding to [0.16.2 on pkg.go.dev](https://pkg.go.dev/vitess.io/vitess@v0.16.2)

### Workarounds
- Always use `vtctldclient` to create shards, instead of using VTAdmin
- Disable creating shards from VTAdmin using RBAC
- Delete the topology record for the offending shard using the client for your topology server. For example, if you created a shard called `a/b` in keyspace `commerce`, and you are running etcd, it can be deleted by doing something like
```
% etcdctl --endpoints "http://${ETCD_SERVER}" del /vitess/global/keyspaces/commerce/shards/a/b/Shard
```

### References
https://github.com/vitessio/vitess/issues/12842

Found during a security audit sponsored by the [CNCF](https://cncf.io) and facilitated by [OSTIF](https://ostif.org).

## References
- https://github.com/vitessio/vitess/security/advisories/GHSA-pqj7-jx24-wj7w
- https://nvd.nist.gov/vuln/detail/CVE-2023-29195
- https://github.com/vitessio/vitess/issues/12842
- https://github.com/vitessio/vitess/pull/12843
- https://github.com/vitessio/vitess/commit/9dcbd7de3180f47e94f54989fb5c66daea00c920
- https://github.com/vitessio/vitess
- https://github.com/vitessio/vitess/releases/tag/v16.0.2
- https://pkg.go.dev/vitess.io/vitess@v0.16.2
