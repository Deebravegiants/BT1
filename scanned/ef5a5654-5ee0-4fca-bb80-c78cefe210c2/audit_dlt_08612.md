# [?] fix bigint overflow bug

## Summary
Severity: Unknown
Chain: Filecoin
Component: filecoin-project/lotus
Published: 2023-08-09
Source: https://github.com/filecoin-project/lotus/commit/84d9dc5dfe9cbe41f834c16ca72a4becb05ad1d7
Type: security-commit

## Details
fix bigint overflow bug

## Patch
### storage/paths/index.go
```diff
@@ -1282,8 +1282,6 @@ func (i *Index) StorageInfo(ctx context.Context, id storiface.ID) (storiface.Sto
 	i.lk.RLock()
 	defer i.lk.RUnlock()
 
-	log.Errorf("StorageInfo called id: ", id)
-
 	si, found := i.stores[id]
 	if !found {
 		return storiface.StorageInfo{}, xerrors.Errorf("sector store not found")
@@ -1341,7 +1339,7 @@ func (dbi *DBIndex) StorageBestAlloc(ctx context.Context, allocate storiface.Sec
 						 where %s and available >= $1
 						 and NOW()-last_heartbeat < $2 
 						 and heartbeat_err is null
-						 order by available * weight desc`, checkString)
+						order by (available::numeric * weight) desc`, checkString)
 	err = dbi.harmonyDB.Select(ctx, &rows,
 		sql, spaceReq, SkippedHeartbeatThresh)
 	if err != nil {
```
