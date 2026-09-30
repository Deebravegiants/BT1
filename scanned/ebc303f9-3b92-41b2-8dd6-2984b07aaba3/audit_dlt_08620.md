# [?] fix: splitstore: Don't deadlock in mpool protector

## Summary
Severity: Unknown
Chain: Filecoin
Component: filecoin-project/lotus
Published: 2022-12-17
Source: https://github.com/filecoin-project/lotus/commit/156ba420c320dfda8cee5d5281c0810490c4be9c
Type: security-commit

## Details
fix: splitstore: Don't deadlock in mpool protector

## Patch
### chain/messagepool/messagepool.go
```diff
@@ -443,8 +443,12 @@ func New(ctx context.Context, api Provider, ds dtypes.MetadataDS, us stmgr.Upgra
 	return mp, nil
 }
 
-func (mp *MessagePool) ForEachPendingMessage(f func(cid.Cid) error) error {
-	mp.lk.Lock()
+func (mp *MessagePool) TryForEachPendingMessage(f func(cid.Cid) error) error {
+	// avoid deadlocks in splitstore compaction when something else needs to access the blockstore
+	// while holding the mpool lock
+	if !mp.lk.TryLock() {
+		return xerrors.Errorf("mpool TryForEachPendingMessage: could not acquire lock")
+	}
 	defer mp.lk.Unlock()
 
 	for _, mset := range mp.pending {
```

### node/modules/chain.go
```diff
@@ -69,7 +69,7 @@ func MessagePool(lc fx.Lifecycle, mctx helpers.MetricsCtx, us stmgr.UpgradeSched
 			return mp.Close()
 		},
 	})
-	protector.AddProtector(mp.ForEachPendingMessage)
+	protector.AddProtector(mp.TryForEachPendingMessage)
 	return mp, nil
 }
 
```
