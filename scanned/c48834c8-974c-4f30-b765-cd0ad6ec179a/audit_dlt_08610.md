# [?] fix: add lk.Lock() and move the map copy to avoid miner crash

## Summary
Severity: Unknown
Chain: Filecoin
Component: filecoin-project/lotus
Published: 2023-11-03
Source: https://github.com/filecoin-project/lotus/commit/c0c4e6bf35dd4ff74670bd264a7acdf5737fc09f
Type: security-commit

## Details
fix: add lk.Lock() and move the map copy to avoid miner crash

## Patch
### node/impl/storminer.go
```diff
@@ -338,15 +338,7 @@ func (sm *StorageMinerAPI) SectorsListInStates(ctx context.Context, states []api
 
 // Use SectorsSummary from stats (prometheus) for faster result
 func (sm *StorageMinerAPI) SectorsSummary(ctx context.Context) (map[api.SectorState]int, error) {
-	sectorStats := sm.Miner.SectorsSummary(ctx)
-	out := make(map[api.SectorState]int)
-
-	for st, count := range sectorStats {
-		state := api.SectorState(st)
-		out[state] = int(count)
-	}
-
-	return out, nil
+	return sm.Miner.SectorsSummary(ctx), nil
 }
 
 func (sm *StorageMinerAPI) StorageLocal(ctx context.Context) (map[storiface.ID]string, error) {
```

### storage/pipeline/sealing.go
```diff
@@ -304,8 +304,18 @@ func (m *Sealing) TerminateSector(ctx context.Context, sid abi.SectorNumber) err
 	return m.sectors.Send(uint64(sid), SectorTerminate{})
 }
 
-func (m *Sealing) SectorsSummary(ctx context.Context) map[SectorState]int64 {
-	return m.stats.byState
+func (m *Sealing) SectorsSummary(ctx context.Context) map[api.SectorState]int {
+	m.stats.lk.Lock()
+	defer m.stats.lk.Unlock()
+
+	out := make(map[api.SectorState]int)
+
+	for st, count := range m.stats.byState {
+		state := api.SectorState(st)
+		out[state] = int(count)
+	}
+
+	return out
 }
 
 func (m *Sealing) TerminateFlush(ctx context.Context) (*cid.Cid, error) {
```
