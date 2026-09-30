# [?] kaiax/valset: Fix selectRandaoCommittee out of bounds

## Summary
Severity: Unknown
Chain: Kaia
Component: kaiachain/kaia
Published: 2024-12-26
Source: https://github.com/kaiachain/kaia/commit/716a17336dcbe2b8b5258b6267e1c1abcb2b12ae
Type: security-commit

## Details
kaiax/valset: Fix selectRandaoCommittee out of bounds

## Patch
### kaiax/valset/impl/getter_context.go
```diff
@@ -158,12 +158,16 @@ func selectRandaoCommittee(qualified *valset.AddressSet, committeeSize uint64, p
 	// Because, the resulting committee will be one validator, and the only validator is also selected as the proposer.
 	// Therefore no special handling for committeeSize == 1 is needed.
 	mixHash := prevMixHash
-	if prevMixHash == nil || len(prevMixHash) == 0 {
+	if len(prevMixHash) == 0 { // At exactly Randao hardfork block, or genesis block, prevMixHash is empty.
 		mixHash = params.ZeroMixHash
 	}
 	seed := valset.HashToSeed(mixHash)
 	shuffled := qualified.ShuffledList(seed)
-	return shuffled[:committeeSize]
+	if len(shuffled) < int(committeeSize) {
+		return shuffled
+	} else {
+		return shuffled[:committeeSize]
+	}
 }
 
 func (v *ValsetModule) getProposer(c *blockContext, round uint64) (common.Address, error) {
```
