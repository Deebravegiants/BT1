# [?] Fix nil dereference deploying contract with value (#946)

## Summary
Severity: Unknown
Chain: Celo
Component: celo-org/celo-blockchain
Published: 2020-03-31
Source: https://github.com/celo-org/celo-blockchain/commit/d73efb5e8b61743aa24208090c13144a81a5c5df
Type: security-commit

## Details
Fix nil dereference deploying contract with value (#946)

* Fix nil dereference deploying contract with value

* Allow transfers to new contracts from whitelisted addresses

## Patch
### core/tx_pool.go
```diff
@@ -609,16 +609,24 @@ func (pool *TxPool) validateTx(tx *types.Transaction, local bool) error {
 
 	// Ensure gold transfers are whitelisted if transfers are frozen.
 	if tx.Value().Sign() > 0 {
-		to := *tx.To()
 		if isFrozen, err := freezer.IsFrozen(params.GoldTokenRegistryId, nil, nil); err != nil {
 			log.Warn("Error determining if transfers are frozen, will proceed as if they are not", "err", err)
 		} else if isFrozen {
 			log.Info("Transfers are frozen")
-			if !transfer_whitelist.IsWhitelisted(to, from, nil, nil) {
-				log.Debug("Attempt to transfer between non-whitelisted addresses", "hash", tx.Hash(), "to", to, "from", from)
-				return ErrTransfersFrozen
+			if tx.To() == nil {
+				if !transfer_whitelist.IsWhitelisted(from, from, nil, nil) {
+					log.Debug("Attempt to transfer to new contract from non-whitelisted address", "hash", tx.Hash(), "from", from)
+					return ErrTransfersFrozen
+				}
+				log.Info("New contract transfer is whitelisted", "hash", tx.Hash(), "from", from)
+			} else {
+				to := *tx.To()
+				if !transfer_whitelist.IsWhitelisted(to, from, nil, nil) {
+					log.Debug("Attempt to transfer between non-whitelisted addresses", "hash", tx.Hash(), "to", to, "from", from)
+					return ErrTransfersFrozen
+				}
+				log.Info("Transfer is whitelisted", "hash", tx.Hash(), "to", to, "from", from)
 			}
-			log.Info("Transfer is whitelisted", "hash", tx.Hash(), "to", to, "from", from)
 		}
 	}
 
```
