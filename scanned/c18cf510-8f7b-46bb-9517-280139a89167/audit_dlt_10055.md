# [?] Merge pull request #7198 from multiversx/fixed-vulnerabilities

## Summary
Severity: Unknown
Chain: MultiversX
Component: multiversx/mx-chain-go
Published: 2025-08-25
Source: https://github.com/multiversx/mx-chain-go/commit/82dabd54b75a1cff0880a6dcf1c77f55681e3240
Type: security-commit

## Details
Merge pull request #7198 from multiversx/fixed-vulnerabilities

TxPool fixes

## Patch
### txcache/selection.go
```diff
@@ -96,6 +96,7 @@ func selectTransactionsFromBunches(
 			selectedTransactions = append(selectedTransactions, selectedTransaction)
 			err := virtualSession.accumulateConsumedBalance(selectedTransaction)
 			if err != nil {
+				// TODO brainstorm whether we should select / not select the transaction on this flow.
 				log.Warn("TxCache.selectTransactionsFromBunches error when accumulating consumed balance",
 					"err", err,
 					"txHash", selectedTransaction.TxHash)
```

### txcache/selectionTracker.go
```diff
@@ -11,6 +11,7 @@ import (
 )
 
 // TODO use a map instead of slice for st.blocks
+// TODO add an upper bound MaxTrackedBlocks
 type selectionTracker struct {
 	mutTracker     sync.RWMutex
 	latestNonce    uint64
@@ -33,6 +34,8 @@ func NewSelectionTracker(txCache txCacheForSelectionTracker) (*selectionTracker,
 
 // OnProposedBlock notifies when a block is proposed and updates the state of the selectionTracker
 // TODO the selection session might be unusable in the flow of OnProposed
+// TODO log in case MaxTrackedBlocks is reached and brainstorm how to solve this case
+// TODO assure minimum blocks validation when adding a proposed block (i.e nonce continuity)
 func (st *selectionTracker) OnProposedBlock(
 	blockHash []byte,
 	blockBody *block.Body,
```

### txcache/txCache.go
```diff
@@ -151,6 +151,7 @@ func (cache *TxCache) SelectTransactions(
 		"gas", accumulatedGas,
 	)
 
+	// TODO drop the diagnoseCounters
 	go cache.diagnoseCounters()
 	go displaySelectionOutcome(logSelect, "selection", transactions)
 
```

### txcache/virtualSelectionSession.go
```diff
@@ -27,7 +27,7 @@ func (virtualSession *virtualSelectionSession) getRecord(address []byte) (*virtu
 
 	virtualRecord, err := virtualSession.createAccountRecord(address)
 	if err != nil {
-		log.Debug("virtualSelectionSession.getRecord: error when creating virtual account record",
+		log.Warn("virtualSelectionSession.getRecord: error when creating virtual account record",
 			"address", address,
 			"err", err)
 		return nil, err
```

### txcache/wrappedTransaction.go
```diff
@@ -33,7 +33,9 @@ func (wrappedTx *WrappedTransaction) precomputeFields(host MempoolHost) {
 
 	gasLimit := wrappedTx.Tx.GetGasLimit()
 	if gasLimit != 0 {
-		wrappedTx.PricePerUnit = wrappedTx.Fee.Uint64() / gasLimit
+		pricePerUnit := big.NewInt(0)
+		_ = pricePerUnit.Div(wrappedTx.Fee, big.NewInt(int64(gasLimit)))
+		wrappedTx.PricePerUnit = pricePerUnit.Uint64()
 	}
 
 	wrappedTx.TransferredValue = host.GetTransferredValue(wrappedTx.Tx)
```
