# [?] api: ethrpc: fix a potential panic when querying block info (#9593)

## Summary
Severity: Unknown
Chain: Filecoin
Component: filecoin-project/lotus
Published: 2022-11-07
Source: https://github.com/filecoin-project/lotus/commit/2e5de478a6ce422a9305465d650e24ccc4a919ca
Type: security-commit

## Details
api: ethrpc: fix a potential panic when querying block info (#9593)

## Patch
### node/impl/full/eth.go
```diff
@@ -659,7 +659,7 @@ func (a *EthModule) ethBlockFromFilecoinTipSet(ctx context.Context, ts *types.Ti
 	for _, blkMsg := range blkMsgs {
 		for _, msg := range append(blkMsg.BlsMessages, blkMsg.SecpkMessages...) {
 			msgLookup, err := a.StateAPI.StateSearchMsg(ctx, types.EmptyTSK, msg.Cid(), api.LookbackNoLimit, true)
-			if err != nil {
+			if err != nil || msgLookup == nil {
 				return api.EthBlock{}, nil
 			}
 			gasUsed += msgLookup.Receipt.GasUsed
```
