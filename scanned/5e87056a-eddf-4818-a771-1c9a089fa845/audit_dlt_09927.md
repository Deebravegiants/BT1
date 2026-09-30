# [?] Merge pull request #77 from yoomee1313/fix-crashing-methods

## Summary
Severity: Unknown
Chain: Kaia
Component: kaiachain/kaia
Published: 2024-09-05
Source: https://github.com/kaiachain/kaia/commit/1cf2543dce3249a88107de55f31b30abd1b8d499
Type: security-commit

## Details
Merge pull request #77 from yoomee1313/fix-crashing-methods

api: do not crash with unknown blocknumber input

## Patch
### governance/api.go
```diff
@@ -86,7 +86,7 @@ func (api *GovernanceKaiaAPI) NodeAddress() common.Address {
 // GetRewards returns detailed information of the block reward at a given block number.
 func (api *GovernanceKaiaAPI) GetRewards(num *rpc.BlockNumber) (*reward.RewardSpec, error) {
 	blockNumber := uint64(0)
-	if num == nil || *num == rpc.LatestBlockNumber {
+	if num == nil || *num == rpc.LatestBlockNumber || *num == rpc.PendingBlockNumber {
 		blockNumber = api.chain.CurrentBlock().NumberU64()
 	} else {
 		blockNumber = uint64(num.Int64())
@@ -365,8 +365,11 @@ func checkStateForStakingInfo(governance Engine, blockNumber uint64) error {
 	if !governance.BlockChain().Config().IsKaiaForkEnabled(big.NewInt(int64(blockNumber + 1))) {
 		return nil
 	}
-
-	_, err := governance.BlockChain().StateAt(governance.BlockChain().GetHeaderByNumber(blockNumber).Root)
+	header := governance.BlockChain().GetHeaderByNumber(blockNumber)
+	if header == nil {
+		return errUnknownBlock
+	}
+	_, err := governance.BlockChain().StateAt(header.Root)
 	return err
 }
 
```
