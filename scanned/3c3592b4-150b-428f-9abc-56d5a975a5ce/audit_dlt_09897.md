# [?] fix panic cause by metrics label mismatch (#112)

## Summary
Severity: Unknown
Chain: IoTeX
Component: iotexproject/iotex-core
Published: 2018-09-27
Source: https://github.com/iotexproject/iotex-core/commit/bbcbe51bdb9f32bfa61856caed02be20570a78c7
Type: security-commit

## Details
fix panic cause by metrics label mismatch (#112)

* change label name

## Patch
### server/itx/heartbeat.go
```diff
@@ -29,7 +29,7 @@ var heartbeatMtc = prometheus.NewGaugeVec(
 		Name: "iotex_heartbeat_status",
 		Help: "Node heartbeat status.",
 	},
-	[]string{"status_type", "chain_id"},
+	[]string{"status_type", "source"},
 )
 
 func init() {
@@ -90,8 +90,8 @@ func (h *HeartbeatHandler) Log() {
 		Str("pendingDispatcherEventsAudit", string(dpEvtsAudit)).
 		Msg("node status")
 
-	heartbeatMtc.WithLabelValues("numPeers").Set(float64(numPeers))
-	heartbeatMtc.WithLabelValues("pendingDispatcherEvents").Set(float64(numDPEvts))
+	heartbeatMtc.WithLabelValues("numPeers", "node").Set(float64(numPeers))
+	heartbeatMtc.WithLabelValues("pendingDispatcherEvents", "node").Set(float64(numDPEvts))
 	// chain service
 	for _, c := range h.s.chainservices {
 		// Consensus metrics
```
