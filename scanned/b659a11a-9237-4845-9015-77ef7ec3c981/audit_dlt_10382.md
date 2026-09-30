# [?] core/txpool/legacypool: fix data race in checkDelegationLimit (#31475)

## Summary
Severity: Unknown
Chain: Ethereum
Component: ethereum/go-ethereum
Published: 2025-03-28
Source: https://github.com/ethereum/go-ethereum/commit/141968a48b45bf343c5921057eca158df5d3c96e
Type: security-commit

## Details
core/txpool/legacypool: fix data race in checkDelegationLimit (#31475)

## Patch
### core/txpool/legacypool/legacypool.go
```diff
@@ -618,7 +618,7 @@ func (pool *LegacyPool) checkDelegationLimit(tx *types.Transaction) error {
 	from, _ := types.Sender(pool.signer, tx) // validated
 
 	// Short circuit if the sender has neither delegation nor pending delegation.
-	if pool.currentState.GetCodeHash(from) == types.EmptyCodeHash && len(pool.all.auths[from]) == 0 {
+	if pool.currentState.GetCodeHash(from) == types.EmptyCodeHash && pool.all.delegationTxsCount(from) == 0 {
 		return nil
 	}
 	pending := pool.pending[from]
@@ -1849,6 +1849,13 @@ func (t *lookup) removeAuthorities(tx *types.Transaction) {
 	}
 }
 
+// delegationTxsCount returns the number of pending authorizations for the specified address.
+func (t *lookup) delegationTxsCount(addr common.Address) int {
+	t.lock.RLock()
+	defer t.lock.RUnlock()
+	return len(t.auths[addr])
+}
+
 // numSlots calculates the number of slots needed for a single transaction.
 func numSlots(tx *types.Transaction) int {
 	return int((tx.Size() + txSlotSize - 1) / txSlotSize)
```
