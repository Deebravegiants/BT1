# [H] etcd: `tlsListener.acceptLoop` spawns unbounded handshake goroutines with no deadline

## Summary
Severity: High
Advisory: GHSA-6vch-q96h-7gc3
CVE: CVE-2026-73500
CWE: CWE-770
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-07-24
Source: https://github.com/advisories/GHSA-6vch-q96h-7gc3
Type: github-advisory

## Affected
- Go: `go.etcd.io/etcd/v3` — affected >=3.7.0-alpha.0 <3.7.1
- Go: `go.etcd.io/etcd/v3` — affected >=3.6.0 <3.6.14
- Go: `go.etcd.io/etcd/v3` — affected >=0 <3.5.33

## Details
### Impact
_What kind of vulnerability is it? Who is impacted?_

A network attacker who can reach an etcd TLS listener can open many TCP connections and never send a ClientHello. Each connection spawns a goroutine in the etcd server process that blocks indefinitely inside tls.Conn.Handshake(), and each is tracked in the pending map. Unbounded goroutine and map growth exhausts memory in the etcd process, causing loss of availability for the etcd cluster (and, when etcd backs Kubernetes, the control plane).

### Patches
_Has the problem been patched? What versions should users upgrade to?_

This vulnerability is patched in the following versions:

- etcd 3.7.1
- etcd 3.6.14
- etcd 3.5.33

### Workarounds
_Is there a way for users to fix or remediate the vulnerability without upgrading?_

If upgrading is not immediately possible, then restrict network access. Limit which hosts can reach etcd's client (gRPC) port via firewall rules or network policy, reducing who can attempt exploitation.

### Reporter

VMware By Broadcom

## References
- https://github.com/etcd-io/etcd/security/advisories/GHSA-6vch-q96h-7gc3
- https://github.com/etcd-io/etcd/pull/22130
- https://github.com/etcd-io/etcd/commit/2e07efce9745004eb4773cffaada9b5cdf77cff2
- https://github.com/etcd-io/etcd/commit/f73cba7d920019f91a1ea1f6697833e42731f057
- https://github.com/etcd-io/etcd
- https://github.com/etcd-io/etcd/releases/tag/v3.5.33
- https://github.com/etcd-io/etcd/releases/tag/v3.6.14
- https://github.com/etcd-io/etcd/releases/tag/v3.7.1
