# [?] node: Fixed potential latest block nil dereference

## Summary
Severity: Unknown
Chain: Wormhole
Component: wormhole-foundation/wormhole
Published: 2022-09-16
Source: https://github.com/wormhole-foundation/wormhole/commit/e31f3e603da25056d8ea1ae705aeafa27e42da45
Type: security-commit

## Details
node: Fixed potential latest block nil dereference

## Patch
### node/pkg/ethereum/pollimpl.go
```diff
@@ -167,13 +167,14 @@ func (e *PollImpl) SubscribeForBlocks(ctx context.Context, sink chan<- *common.N
 
 					// See if the next block has been created yet.
 					if currentBlockNumber.Cmp(latestBlock.Number) > 0 {
-						latestBlock, err = e.getBlock(ctx, nil)
-						if err != nil {
+						tmpLatestBlock, latestBlockErr := e.getBlock(ctx, nil)
+						if latestBlockErr != nil {
 							errorOccurred = true
 							e.logger.Error("failed to look up latest block", zap.String("eth_network", e.BaseEth.NetworkName),
-								zap.Uint64("block", currentBlockNumber.Uint64()), zap.Error(err))
+								zap.Uint64("block", currentBlockNumber.Uint64()), zap.Error(latestBlockErr))
 							break
 						}
+						latestBlock = tmpLatestBlock
 
 						if currentBlockNumber.Cmp(latestBlock.Number) > 0 {
 							// We have to wait for this block to become available.
```
