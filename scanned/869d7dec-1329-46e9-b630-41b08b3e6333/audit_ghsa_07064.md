# [H] etcd: Watch API authorization bypass via open-ended range requests

## Summary
Severity: High
Advisory: GHSA-xg4h-6gfc-h4m8
CVE: CVE-2026-73499
CWE: CWE-863
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-07-24
Source: https://github.com/advisories/GHSA-xg4h-6gfc-h4m8
Type: github-advisory

## Affected
- Go: `go.etcd.io/etcd/v3` — affected >=3.7.0-alpha.0 <3.7.1
- Go: `go.etcd.io/etcd/v3` — affected >=3.6.0 <3.6.14
- Go: `go.etcd.io/etcd/v3` — affected >=0 <3.5.33

## Details
### Impact
_What kind of vulnerability is it? Who is impacted?_

A user granted READ permission on a single, exact key can use the Watch gRPC API with `clientv3.WithFromKey()` (an open-ended, "from this key to the end of the keyspace" watch) to receive watch events for every key lexicographically greater than or equal to their permitted key — not just the one key they were granted. 

This is an authorization bypass in etcd's RBAC enforcement for the Watch API; Range/Get and DeleteRange requests are not affected. It only affects clusters with authentication enabled — clusters running without auth already allow unrestricted read access.

### Patches
_Has the problem been patched? What versions should users upgrade to?_

This vulnerability is patched in the following versions:

- etcd 3.7.1
- etcd 3.6.14
- etcd 3.5.33

### Workarounds
_Is there a way for users to fix or remediate the vulnerability without upgrading?_

If upgrading is not immediately possible, the following mitigations reduce exposure:

- Audit READ grants. Any READ grant — even on one key — can be leveraged via Watch to read everything after it. Review who holds READ permissions and revoke/tighten any you wouldn't trust with full read access.
- Restrict network access. Limit which hosts can reach etcd's client (gRPC) port via firewall rules or network policy, reducing who can attempt exploitation.

### Reporter

- Luis Toro ([@lobuhi](https://github.com/lobuhi) on Github)
- Anthropic  and Adam Korczynski ([@AdamKorcz](https://github.com/AdamKorcz) on Github)

## References
- https://github.com/etcd-io/etcd/security/advisories/GHSA-xg4h-6gfc-h4m8
- https://github.com/etcd-io/etcd/commit/6643f80602461a6095c9b294b6512fd9719bef41
- https://github.com/etcd-io/etcd/commit/afeaa624da19085b47fb5ccc7c22a8c421bc2eae
- https://github.com/etcd-io/etcd/commit/e863b001bbf3367003a543aa3099db9892134cd7
- https://github.com/etcd-io/etcd
- https://github.com/etcd-io/etcd/releases/tag/v3.5.33
- https://github.com/etcd-io/etcd/releases/tag/v3.6.14
- https://github.com/etcd-io/etcd/releases/tag/v3.7.1
