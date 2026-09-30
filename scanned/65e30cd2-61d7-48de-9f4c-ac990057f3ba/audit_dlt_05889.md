# [?] fix(eth): remove non-deterministic behaviour from eth keeper (#432)

## Summary
Severity: Unknown
Chain: Axelar
Component: axelarnetwork/axelar-core
Published: 2021-04-29
Source: https://github.com/axelarnetwork/axelar-core/commit/5adbee6cec35f0747343ab15e7248ea1e682653c
Type: security-commit

## Details
fix(eth): remove non-deterministic behaviour from eth keeper (#432)

GetDeposit iterated over a map to get the correct deposit. While it was deterministic for our logic (exactly one case would be hit), it's possible that the kvstore in the background spent different amounts of gas on different nodes. This commit removes the loop over the map in favour of rolling out all cases.

## Patch
### x/ethereum/keeper/keeper.go
```diff
@@ -281,20 +281,17 @@ func (k Keeper) SetPendingDeposit(ctx sdk.Context, poll exported.PollMeta, depos
 // GetDeposit retrieves a confirmed/burned deposit
 func (k Keeper) GetDeposit(ctx sdk.Context, txID string, burnAddr string) (types.ERC20Deposit, types.DepositState, bool) {
 	var deposit types.ERC20Deposit
-	prefixes := map[types.DepositState]string{
-		types.CONFIRMED: confirmedDepositPrefix,
-		types.BURNED:    burnedDepositPrefix,
-	}
 
-	// the order of this iteration is non-deterministic,
-	// the only reason this is correct is because exactly one of the cases is true
-	for state, prefix := range prefixes {
-		bz := ctx.KVStore(k.storeKey).Get([]byte(prefix + txID + "_" + burnAddr))
-		if bz != nil {
-			k.cdc.MustUnmarshalBinaryLengthPrefixed(bz, &deposit)
-			return deposit, state, true
-		}
+	bz := ctx.KVStore(k.storeKey).Get([]byte(confirmedDepositPrefix + txID + "_" + burnAddr))
+	if bz != nil {
+		k.cdc.MustUnmarshalBinaryLengthPrefixed(bz, &deposit)
+		return deposit, types.CONFIRMED, true
+	}
 
+	bz = ctx.KVStore(k.storeKey).Get([]byte(burnedDepositPrefix + txID + "_" + burnAddr))
+	if bz != nil {
+		k.cdc.MustUnmarshalBinaryLengthPrefixed(bz, &deposit)
+		return deposit, types.BURNED, true
 	}
 
 	return types.ERC20Deposit{}, 0, false
```
