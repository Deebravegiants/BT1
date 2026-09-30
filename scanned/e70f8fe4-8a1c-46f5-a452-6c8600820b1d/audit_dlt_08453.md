# [?] fix(nodebuilder/p2p): fix autonat == nil panic in test (#4170)

## Summary
Severity: Unknown
Chain: Celestia
Component: celestiaorg/celestia-node
Published: 2025-03-17
Source: https://github.com/celestiaorg/celestia-node/commit/b1530887dbc4a56b71e894b5a280321098f4fb8d
Type: security-commit

## Details
fix(nodebuilder/p2p): fix autonat == nil panic in test (#4170)

Co-authored-by: Oleg Kovalov <oleg@hey.com>

## Patch
### nodebuilder/p2p/reachability.go
```diff
@@ -14,7 +14,12 @@ func reachabilityCheck(ctx context.Context, host HostBase) {
 	if !ok {
 		panic("host does not implement autoNatGetter")
 	}
+
 	autoNAT := getter.GetAutoNat()
+	if autoNAT == nil {
+		log.Error("autoNAT is nil on host")
+		return
+	}
 
 	go func() {
 		ticker := time.NewTicker(reachabilityCheckTick)
```
