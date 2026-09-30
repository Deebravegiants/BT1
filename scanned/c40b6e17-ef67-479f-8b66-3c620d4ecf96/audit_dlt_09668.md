# [?] fix: potential int overflow when creating sequencers (#704)

## Summary
Severity: Unknown
Chain: Dymension
Component: dymensionxyz/dymension
Published: 2024-03-20
Source: https://github.com/dymensionxyz/dymension/commit/d254fe2a9fe98c47e316a0276dba9ca345129181
Type: security-commit

## Details
fix: potential int overflow when creating sequencers (#704)

## Patch
### x/sequencer/keeper/msg_server_create_sequencer.go
```diff
@@ -92,7 +92,7 @@ func (k msgServer) CreateSequencer(goCtx context.Context, msg *types.MsgCreateSe
 	sequencersByRollapp := k.GetSequencersByRollappByStatus(ctx, msg.RollappId, types.Bonded)
 	// check to see if we reached the maximum number of sequencers for this rollapp
 	currentNumOfSequencers := len(sequencersByRollapp)
-	if currentNumOfSequencers >= int(rollapp.MaxSequencers) {
+	if uint64(currentNumOfSequencers) >= rollapp.MaxSequencers {
 		return nil, types.ErrMaxSequencersLimit
 	}
 	// this is the first sequencer, make it a PROPOSER
```
