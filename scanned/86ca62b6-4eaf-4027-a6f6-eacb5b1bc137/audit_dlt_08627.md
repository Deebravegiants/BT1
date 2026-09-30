# [?] sealing: Avoid panicking in handleUpdateActivating on startup

## Summary
Severity: Unknown
Chain: Filecoin
Component: filecoin-project/lotus
Published: 2022-09-19
Source: https://github.com/filecoin-project/lotus/commit/66ad2b810237382e2365092ec606004ecd97acb6
Type: security-commit

## Details
sealing: Avoid panicking in handleUpdateActivating on startup

## Patch
### storage/pipeline/states_replica_update.go
```diff
@@ -240,6 +240,10 @@ func (m *Sealing) handleFinalizeReplicaUpdate(ctx statemachine.Context, sector S
 }
 
 func (m *Sealing) handleUpdateActivating(ctx statemachine.Context, sector SectorInfo) error {
+	if sector.ReplicaUpdateMessage == nil {
+		return xerrors.Errorf("nil sector.ReplicaUpdateMessage!")
+	}
+
 	try := func() error {
 		mw, err := m.Api.StateWaitMsg(ctx.Context(), *sector.ReplicaUpdateMessage, build.MessageConfidence, api.LookbackNoLimit, true)
 		if err != nil {
```
