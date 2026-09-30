# [?] fix(metrics): disable otel exemplars to prevent rune overflow (#11211)

## Summary
Severity: Unknown
Chain: IPFS
Component: ipfs/kubo
Published: 2026-02-25
Source: https://github.com/ipfs/kubo/commit/f55bbdd539cb50c80ad7ecc1c68bd9c10340a8b7
Type: security-commit

## Details
fix(metrics): disable otel exemplars to prevent rune overflow (#11211)

* fix: disable otel exemplars to prevent prometheus rune overflow

the OTel SDK View from #11208 drops server.address from http.server.*
metric labels, but the OTel spec requires filtered attributes to be
carried as exemplar FilteredAttributes. on subdomain gateways the
server.address value (e.g. "CID.ipfs.dweb.link") combined with
trace_id and span_id exceeds the 128-rune prometheus exemplar limit.

- cmd/ipfs/kubo/daemon.go: add exemplar.AlwaysOffFilter to MeterProvider
- docs/changelogs/v0.40.md: document exemplar disable in metrics section

(cherry picked from commit 221741ee20581a0968b3989adab4e44fbcf9a527)

## Patch
### cmd/ipfs/kubo/daemon.go
```diff
@@ -47,6 +47,7 @@ import (
 	"go.opentelemetry.io/otel/attribute"
 	promexporter "go.opentelemetry.io/otel/exporters/prometheus"
 	sdkmetric "go.opentelemetry.io/otel/sdk/metric"
+	"go.opentelemetry.io/otel/sdk/metric/exemplar"
 )
 
 const (
@@ -239,6 +240,14 @@ func daemonFunc(req *cmds.Request, re cmds.ResponseEmitter, env cmds.Environment
 					),
 				},
 			)),
+			// Disable exemplars. The OTel spec requires exemplars to carry
+			// attributes filtered out by Views (as FilteredAttributes).
+			// The server.address value on subdomain gateways (e.g.
+			// "CID.ipfs.dweb.link") combined with trace_id and span_id
+			// exceeds the 128-rune Prometheus exemplar limit.
+			// Re-enabling exemplars requires removing all metrics that
+			// track server.address (the above View is not enough).
+			sdkmetric.WithExemplarFilter(exemplar.AlwaysOffFilter),
 			sdkmetric.WithReader(exporter),
 		)
 		otel.SetMeterProvider(meterProvider)
```

### docs/changelogs/v0.40.md
```diff
@@ -307,8 +307,10 @@ Most Kubo users are unaffected by this change. It matters if you run Kubo as a p
 
 **What changed:**
 
-- The unbounded `server_address` label is now dropped from all `http_server_*` metrics via an OTel SDK View.
-- All handlers add a `server_domain` label instead. Gateway handlers group by matching `Gateway.PublicGateways` suffix (e.g., `dweb.link`, `ipfs.io`), with `localhost`, `loopback`, or `other` for unmatched hosts. The RPC API and Libp2p Gateway handlers use fixed values (`api`, `libp2p`).
+- `http_server_*` metrics replace the unbounded `server_address` label with a new `server_domain` label that groups requests by gateway domain:
+  - Gateway: matched [`Gateway.PublicGateways`](https://github.com/ipfs/kubo/blob/master/docs/config.md#gatewaypublicgateways) suffix (e.g., `dweb.link`, `ipfs.io`), or `localhost`, `loopback`, `other`
+  - RPC API: `api` / Libp2p Gateway: `libp2p`
+- Prometheus exemplars are disabled to prevent log noise from long subdomain hostnames. Tracing spans are unaffected.
 
 If you use [Rainbow](https://github.com/ipfs/rainbow) for your public gateway (recommended), this issue never applied to you -- Rainbow uses its own low-cardinality HTTP metrics.
 
```
