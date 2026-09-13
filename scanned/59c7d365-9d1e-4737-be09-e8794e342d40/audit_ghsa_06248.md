# [M] arc has unauthenticated cluster node admission when `cluster.shared_secret` is unset

## Summary
Severity: Medium
Advisory: GHSA-p378-jp5r-gpgw
CVE: CVE-2026-55678
CWE: CWE-284, CWE-287, CWE-306
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-08-28
Source: https://github.com/advisories/GHSA-p378-jp5r-gpgw
Type: github-advisory

## Affected
- Go: `github.com/basekick-labs/arc` — affected >=0 <0.0.0-20260615160325-38402ad2ebdd

## Details
## Summary

Arc Enterprise clustering accepts cluster join requests without authentication when `cluster.enabled=true` but `cluster.shared_secret` is not configured. The coordinator validates HMAC authentication only if a shared secret is non-empty; otherwise, a network attacker who can reach the coordinator port can send a join request with attacker-controlled node addresses and role. Accepted nodes are marked healthy, registered locally or added as Raft voters, and can be selected by the 
cluster router for forwarded authenticated requests.

## Details

Cluster defaults include an empty shared secret and TLS disabled:

- `internal/config/config.go:943-950` defaults `cluster.enabled=false`, `cluster.cluster_name="arc-cluster"`, and `cluster.coordinator_addr=":9100"`.
- `internal/config/config.go:1001-1005` defaults `cluster.shared_secret=""` and `cluster.tls_enabled=false`.

Startup requires a shared secret only for file replication, not for all clustering/join/routing use:

- `cmd/arc/main.go:1258-1265` hard-fails without `cluster.shared_secret` only when `cluster.replication_enabled` is true.

The join request contains attacker-supplied node identity, role, and addresses:

- `internal/cluster/protocol/messages.go:127-142` defines `JoinRequest` fields including `node_id`, `role`, `raft_addr`, `api_addr`, `coord_addr`, plus optional auth fields.

The coordinator validates HMAC only when the configured shared secret is non-empty:

- `internal/cluster/coordinator.go:1066-1081` wraps all HMAC checks in `if c.cfg.SharedSecret != "" { ... }`.
- If the secret is empty, the join request proceeds after only the cluster-name check.

An accepted join creates a healthy node from attacker-controlled fields and adds it to cluster trust state:

- `internal/cluster/coordinator.go:1101-1107` creates a node from request fields, sets attacker-provided coordinator/API addresses, and marks it healthy.
- `internal/cluster/coordinator.go:1108-1129` adds the attacker-provided `raft_addr` as a Raft voter and stores node info when Raft is configured.
- `internal/cluster/coordinator.go:1133-1138` registers the node locally when Raft is not configured.

The router uses healthy nodes from this registry and forwards authenticated requests to their advertised API addresses:

- `internal/cluster/registry.go:263-270` returns healthy writers/readers.
- `internal/cluster/router.go:154-177` routes writes to healthy writer nodes.
- `internal/cluster/router.go:203-227` routes queries to healthy readers, or writers if no readers exist.
- `internal/cluster/router.go:327-357` builds the forwarding target from `node.APIAddress` and copies all original request headers to the peer, including `Authorization` and `x-api-key`.
- `cmd/arc/main.go:1887-1897` wires the cluster router into MessagePack, line protocol, TLE, and query handlers when the cluster coordinator exists.

A related lower-severity issue is that heartbeat messages are also unauthenticated:

- `internal/cluster/protocol/messages.go:175-180` defines `Heartbeat` without HMAC fields.
- `internal/cluster/coordinator.go:1220-1232` records heartbeats and updates node state based only on supplied `node_id` and `state`.

## Proof of concept

Safe local lab reproduction only; do not target external infrastructure.

Prerequisites:

- Enterprise clustering enabled in a lab deployment.
- `cluster.shared_secret` intentionally left empty.
- Network access to the coordinator TCP port, default `9100`.
- The attacker knows or guesses the cluster name; default is `arc-cluster`.

Steps:

1. Start an Arc cluster node with:

```toml
[cluster]
enabled = true
cluster_name = "arc-cluster"
coordinator_addr = ":9100"
shared_secret = ""
tls_enabled = false
```

2. Start an attacker-controlled HTTP listener that records request method, path, and headers, for example on `127.0.0.1:18080`.

3. Send a framed cluster join request to the victim coordinator. The protocol uses a 4-byte big-endian length prefix, followed by a 1-byte message type (`MsgJoinRequest == 1`), followed by JSON. The payload should include attacker-controlled node fields and omit `auth_nonce`, `auth_timestamp`, and `auth_hmac`:

```json
{
  "node_id": "evil-reader-1",
  "node_name": "evil-reader",
  "role": "reader",
  "cluster_name": "arc-cluster",
  "raft_addr": "127.0.0.1:19020",
  "api_addr": "127.0.0.1:18080",
  "coord_addr": "127.0.0.1:19010",
  "version": "lab",
  "core_count": 1
}
```

Expected vulnerable result: the coordinator accepts the join instead of rejecting it for missing authentication.

4. Trigger a forwarded operation from a node that cannot handle the operation locally. Examples depend on cluster roles:

- Join as `reader` and trigger a query through a node that routes queries to readers.
- Join as `writer` and trigger ingestion through a non-writer node that routes writes to writers.

Expected vulnerable result: the attacker-controlled HTTP listener receives forwarded requests. Because `forwardRequest` copies all original headers, the listener can observe authentication headers such as bearer tokens or API keys along with request paths and bodies.

5. In a Raft-enabled lab, observe that the attacker-provided `raft_addr` is submitted to `AddVoter`, demonstrating unauthorized membership mutation.

## Impact

In affected cluster deployments, an unauthenticated network attacker can become a trusted cluster node. Practical impacts include:

- Interception of forwarded authenticated HTTP requests, including `Authorization` and `x-api-key` headers.
- Exposure of query bodies, ingestion data, database/measurement names, and operational metadata.
- Unauthorized cluster membership mutation, including attempted Raft voter addition when Raft is configured.
- Potential data integrity impact if the rogue node returns forged query/write responses or accepts/diverts writes.
- Potential availability impact by blackholing or delaying forwarded operations.

This is not reachable in the default standalone configuration because `cluster.enabled=false`, but it is a critical trust-boundary issue for Enterprise cluster deployments where clustering is enabled without a shared secret. The code already treats `cluster.shared_secret` as mandatory for replication, which suggests unauthenticated cluster membership should also fail closed.


## Suggested fix

- Fail startup when `cluster.enabled=true` and `cluster.shared_secret` is empty, not only when `cluster.replication_enabled=true`.
- Reject all trust-mutating coordinator messages when no cluster authentication is configured, including join, heartbeat/state update, forward apply, and file replication messages.
- Require HMAC or mutual TLS before processing any join/heartbeat message.
- Bind authentication to node identity and advertised addresses to reduce replay and address-substitution risks.
- Do not forward end-user `Authorization`/`x-api-key` headers to a peer unless the peer identity has been authenticated and authorized.
- Add tests proving unauthenticated join and heartbeat requests fail when clustering is enabled.

## References / evidence

- `internal/config/config.go:943-950`
- `internal/config/config.go:1001-1005`
- `cmd/arc/main.go:1258-1265`
- `internal/cluster/protocol/messages.go:127-142`
- `internal/cluster/coordinator.go:1066-1081`
- `internal/cluster/coordinator.go:1101-1138`
- `internal/cluster/router.go:154-177`
- `internal/cluster/router.go:203-227`
- `internal/cluster/router.go:327-357`
- `cmd/arc/main.go:1887-1897`

## References
- https://github.com/Basekick-Labs/arc/security/advisories/GHSA-p378-jp5r-gpgw
- https://github.com/Basekick-Labs/arc/pull/505
- https://github.com/Basekick-Labs/arc/commit/38402ad2ebddd32c15bf4a0fc9c22c920e5685df
- https://github.com/Basekick-Labs/arc
- https://github.com/Basekick-Labs/arc/releases/tag/v26.06.2
