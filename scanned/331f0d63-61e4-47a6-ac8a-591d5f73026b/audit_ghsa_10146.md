# [M] kube-router: BGP Peer Passwords Exposed in Logs at Verbose Logging Level

## Summary
Severity: Medium
Advisory: GHSA-fcmh-qfxc-w685
CWE: CWE-532
Ecosystem: Go
CVSS: CVSS:3.1/AV:L/AC:H/PR:H/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-04-08
Source: https://github.com/advisories/GHSA-fcmh-qfxc-w685
Type: github-advisory

## Affected
- Go: `github.com/cloudnativelabs/kube-router/v2` — affected >=2.7.0

## Details
## Summary

When kube-router is configured with per-node BGP peer passwords using the `kube-router.io/peer.passwords` node annotation, and verbose logging is enabled (`--v=2` or higher), the raw Kubernetes node annotation map is logged verbatim — including the base64-encoded BGP MD5 passwords. Anyone with access to kube-router's logs (via `kubectl logs`, log aggregation systems, or shared log dumps during debugging) can extract and decode the BGP peer passwords. The official troubleshooting documentation instructs users to collect logs at `-v=2` before filing issues, making accidental disclosure during support interactions a realistic scenario.

## Details

The vulnerability is at `pkg/controllers/routing/network_routes_controller.go:1129`:

```go
// pkg/controllers/routing/network_routes_controller.go:1127-1133
// If the global routing peer is configured then peer with it
// else attempt to get peers from node specific BGP annotations.
if len(nrc.globalPeerRouters) == 0 {
    klog.V(2).Infof("Attempting to construct peer configs from annotation: %+v", node.Annotations)
    peerCfgs, err := bgpPeerConfigsFromAnnotations(
```

`node.Annotations` is of type `map[string]string`. This type does not implement `fmt.Stringer`, so `%+v` formatting dumps every key-value pair verbatim. When `kube-router.io/peer.passwords` is set on the node (the documented mechanism for providing per-node BGP MD5 passwords), its base64-encoded value appears in the log output.

The BGP peer password annotation is documented in `docs/user-guide.md` and has the constant:

```go
// pkg/controllers/routing/network_routes_controller.go:59
peerPasswordAnnotation = "kube-router.io/peer.passwords"
```

Note that a password-safe `String()` method exists on `PeerConfig` and `PeerConfigs` in `pkg/bgp/peer_config.go` and is tested:

```go
// pkg/bgp/peer_config.go:63-79
// Custom Stringer to prevent leaking passwords when printed
func (p PeerConfig) String() string {
    // ...password field is intentionally omitted...
}
```

However, this protective method is never invoked by the vulnerable log statement, which dumps the raw annotation map before any parsing occurs. The password masking only applies after the annotation is parsed into `PeerConfig` structs.

The second log statement at line 1510 (`klog.Infof("Peer config from %s annotation: %+v", peersAnnotation, peerConfigs)`) is **not vulnerable** — `peerConfigs` is of type `bgp.PeerConfigs` which implements `fmt.Stringer` and correctly masks passwords.

The vulnerable path (`bgpPeerConfigsFromIndividualAnnotations`) is triggered when the `kube-router.io/peers` consolidated YAML annotation is not set — i.e., when operators use the older individual annotation format (`kube-router.io/peer.ips`, `kube-router.io/peer.asns`, `kube-router.io/peer.passwords`). This older format remains fully supported and documented.

## PoC

**Setup**: Node has per-node BGP peer annotations including a password:
```bash
kubectl annotate node worker-1 \
  kube-router.io/peer.ips=192.0.2.1 \
  kube-router.io/peer.asns=65001 \
  "kube-router.io/peer.passwords=$(echo -n 's3cr3t-bgp-p@ss' | base64)"
```

**Trigger**: Start kube-router with verbose logging (e.g., following troubleshooting documentation):
```bash
# As documented in docs/troubleshoot.md for debugging:
kube-router ... --v=2
```

**Observe**: In kube-router pod logs:
```
I0318 10:23:41.123456 1 network_routes_controller.go:1129] Attempting to construct peer configs from annotation:
map[
  kube-router.io/peer.asns:65001
  kube-router.io/peer.ips:192.0.2.1
  kube-router.io/peer.passwords:czNjcjN0LWJncC1wQHNz   <-- base64-encoded password
  ...other annotations...
]
```

**Decode the password**:
```bash
echo "czNjcjN0LWJncC1wQHNz" | base64 -d
# Output: s3cr3t-bgp-p@ss
```

**Impact**: With the decoded password and network adjacency to the BGP peer, an attacker can establish an unauthorized BGP session, inject routes, or disrupt legitimate BGP peering.

## Impact

- **BGP credential disclosure**: BGP MD5 authentication passwords are exposed to anyone with access to kube-router log output
- **BGP session hijacking**: An attacker who obtains the password and has network-level access to a BGP neighbor can impersonate the kube-router node, injecting malicious routes into the BGP table
- **Log forwarding risk**: Log aggregation systems (Fluentd, Loki, Elastic, Splunk) typically have different and often broader access controls than Kubernetes RBAC. Passwords aggregated into these systems may be accessible to personnel without Kubernetes node access
- **Support workflow exposure**: The official troubleshooting documentation recommends collecting `--v=2` logs before filing issues, creating a realistic path for passwords to be shared in bug reports or support tickets

## Recommended Fix

Remove or redact the vulnerable log statement at line 1129. The diagnostic information it provides (confirming that annotation-based peer configuration is being used) can be conveyed without exposing credential values:

```go
// Before (vulnerable):
klog.V(2).Infof("Attempting to construct peer configs from annotation: %+v", node.Annotations)

// After (safe):
klog.V(2).Infof("Attempting to construct peer configs from per-node annotations (kube-router.io/peer.ips, etc.)")
```

If full annotation content is needed for debugging (e.g., to show non-sensitive annotations), log a filtered version that explicitly excludes the password annotation:

```go
// Safe alternative that preserves non-sensitive diagnostic info:
safeAnnotations := make(map[string]string)
for k, v := range node.Annotations {
    if k != peerPasswordAnnotation {
        safeAnnotations[k] = v
    }
}
klog.V(2).Infof("Attempting to construct peer configs from annotations: %+v", safeAnnotations)
```

## References
- https://github.com/cloudnativelabs/kube-router/security/advisories/GHSA-fcmh-qfxc-w685
- https://github.com/cloudnativelabs/kube-router
