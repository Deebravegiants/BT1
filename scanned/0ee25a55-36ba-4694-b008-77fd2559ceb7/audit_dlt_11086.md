# [?] op-node: Fix stop sequencer deadlock in op-conductor deployments (#13806)

## Summary
Severity: Unknown
Chain: Boba
Component: bobanetwork/boba
Published: 2025-01-23
Source: https://github.com/bobanetwork/boba/commit/969382a3ff0fb577a7fda6287f3c74f8c26dce53
Type: security-commit

## Details
op-node: Fix stop sequencer deadlock in op-conductor deployments (#13806)

* op-node: Fix stop sequencer deadlock

* fix lint

## Patch
### op-node/rollup/sequencing/sequencer.go
```diff
@@ -672,6 +672,16 @@ func (d *Sequencer) Stop(ctx context.Context) (common.Hash, error) {
 
 	// ensure latestHead has been updated to the latest sealed/gossiped block before stopping the sequencer
 	for d.latestHead.Hash != d.latestSealed.Hash {
+
+		// if we are not the leader, latestSealed will never be updated and we will wait forever
+		if isLeader, err := d.conductor.Leader(ctx); err != nil {
+			d.log.Warn("Could not determine leadership while stopping. Skipping wait.", "err", err)
+			break
+		} else if !isLeader {
+			d.log.Info("Not leader anymore, skipping head sync wait")
+			break
+		}
+
 		latestHeadSet := make(chan struct{})
 		d.latestHeadSet = latestHeadSet
 		d.l.Unlock()
```
