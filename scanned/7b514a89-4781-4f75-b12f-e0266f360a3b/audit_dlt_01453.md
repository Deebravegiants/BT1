# [?] Improve double spend error strings.

## Summary
Severity: Unknown
Chain: Bitcoin
Component: btcsuite/btcd
Published: 2015-01-07
Source: https://github.com/btcsuite/btcd/commit/c257da934e51dabbec5b2397092faed249e7ad26
Type: security-commit

## Details
Improve double spend error strings.

The mempool's MaybeAcceptTransaction methods have also been modified
to return a slice of transaction hashes referenced by the transaction
inputs which are unknown (totally spent or never seen).  While this is
currently used to include the first hash in a ProcessTransaction error
message if inserting orphans is not allowed, it may also be used in
the future to request orphan transactions from peers.

## Patch
### blockmanager.go
```diff
@@ -1176,7 +1176,8 @@ func (b *blockManager) handleNotifyMsg(notification *btcchain.Notification) {
 		// Reinsert all of the transactions (except the coinbase) into
 		// the transaction pool.
 		for _, tx := range block.Transactions()[1:] {
-			err := b.server.txMemPool.MaybeAcceptTransaction(tx, nil, false, true)
+			_, err := b.server.txMemPool.MaybeAcceptTransaction(tx,
+				false, true)
 			if err != nil {
 				// Remove the transaction and all transactions
 				// that depend on it if it wasn't accepted into
```

### log.go
```diff
@@ -30,7 +30,7 @@ const (
 
 	// maxRejectReasonLen is the maximum length of a sanitized reject reason
 	// that will be logged.
-	maxRejectReasonLen = 200
+	maxRejectReasonLen = 250
 )
 
 // Loggers per subsytem.  Note that backendLog is a seelog logger that all of
```

### mempool.go
```diff
@@ -741,8 +741,9 @@ func (txD *TxDesc) CurrentPriority(txStore btcchain.TxStore, nextBlockHeight int
 func (mp *txMemPool) checkPoolDoubleSpend(tx *btcutil.Tx) error {
 	for _, txIn := range tx.MsgTx().TxIn {
 		if txR, exists := mp.outpoints[txIn.PreviousOutPoint]; exists {
-			str := fmt.Sprintf("transaction %v in the pool "+
-				"already spends the same coins", txR.Sha())
+			str := fmt.Sprintf("output %v already spent by "+
+				"transaction %v in the memory pool",
+				txIn.PreviousOutPoint, txR.Sha())
 			return txRuleError(btcwire.RejectDuplicate, str)
 		}
 	}
@@ -799,18 +800,15 @@ func (mp *txMemPool) FetchTransaction(txHash *btcwire.ShaHash) (*btcutil.Tx, err
 // more details.
 //
 // This function MUST be called with the mempool lock held (for writes).
-func (mp *txMemPool) maybeAcceptTransaction(tx *btcutil.Tx, isOrphan *bool, isNew, rateLimit bool) error {
-	if isOrphan != nil {
-		*isOrphan = false
-	}
+func (mp *txMemPool) maybeAcceptTransaction(tx *btcutil.Tx, isNew, rateLimit bool) ([]*btcwire.ShaHash, error) {
 	txHash := tx.Sha()
 
 	// Don't accept the transaction if it already exists in the pool.  This
 	// applies to orphan transactions as well.  This check is intended to
 	// be a quick check to weed out duplicates.
 	if mp.haveTransaction(txHash) {
 		str := fmt.Sprintf("already have transaction %v", txHash)
-		return txRuleError(btcwire.RejectDuplicate, str)
+		return nil, txRuleError(btcwire.RejectDuplicate, str)
 	}
 
 	// Perform preliminary sanity checks on the transaction.  This makes
@@ -819,16 +817,16 @@ func (mp *txMemPool) maybeAcceptTransaction(tx *btcutil.Tx, isOrphan *bool, isNe
 	err := btcchain.CheckTransactionSanity(tx)
 	if err != nil {
 		if cerr, ok := err.(btcchain.RuleError); ok {
-			return chainRuleError(cerr)
+			return nil, chainRuleError(cerr)
 		}
-		return err
+		return nil, err
 	}
 
 	// A standalone transaction must not be a coinbase transaction.
 	if btcchain.IsCoinBase(tx) {
 		str := fmt.Sprintf("transaction %v is an individual coinbase",
 			txHash)
-		return txRuleError(btcwire.RejectInvalid, str)
+		return nil, txRuleError(btcwire.RejectInvalid, str)
 	}
 
 	// Don't accept transactions with a lock time after the maximum int32
@@ -838,7 +836,7 @@ func (mp *txMemPool) maybeAcceptTransaction(tx *btcutil.Tx, isOrphan *bool, isNe
 	if tx.MsgTx().LockTime > math.MaxInt32 {
 		str := fmt.Sprintf("transaction %v has a lock time after "+
 			"2038 which is not accepted yet", txHash)
-		return txRuleError(btcwire.RejectNonstandard, str)
+		return nil, txRuleError(btcwire.RejectNonstandard, str)
 	}
 
 	// Get the current height of the main chain.  A standalone transaction
@@ -848,7 +846,7 @@ func (mp *txMemPool) maybeAcceptTransaction(tx *btcutil.Tx, isOrphan *bool, isNe
 	if err != nil {
 		// This is an unexpected error so don't turn it into a rule
 		// error.
-		return err
+		return nil, err
 	}
 	nextBlockHeight := curHeight + 1
 
@@ -866,7 +864,7 @@ func (mp *txMemPool) maybeAcceptTransaction(tx *btcutil.Tx, isOrphan *bool, isNe
 			}
 			str := fmt.Sprintf("transaction %v is not standard: %v",
 				txHash, err)
-			return txRuleError(rejectCode, str)
+			return nil, txRuleError(rejectCode, str)
 		}
 	}
 
@@ -880,7 +878,7 @@ func (mp *txMemPool) maybeAcceptTransaction(tx *btcutil.Tx, isOrphan *bool, isNe
 	// which examines the actual spend data and prevents double spends.
 	err = mp.checkPoolDoubleSpend(tx)
 	if err != nil {
-		return err
+		return nil, err
 	}
 
 	// Fetch all of the transactions referenced by the inputs to this
@@ -890,32 +888,36 @@ func (mp *txMemPool) maybeAcceptTransaction(tx *btcutil.Tx, isOrphan *bool, isNe
 	txStore, err := mp.fetchInputTransactions(tx)
 	if err != nil {
 		if cerr, ok := err.(btcchain.RuleError); ok {
-			return chainRuleError(cerr)
+			return nil, chainRuleError(cerr)
 		}
-		return err
+		return nil, err
 	}
 
 	// Don't allow the transaction if it exists in the main chain and is not
 	// not already fully spent.
 	if txD, exists := txStore[*txHash]; exists && txD.Err == nil {
 		for _, isOutputSpent := range txD.Spent {
 			if !isOutputSpent {
-				return txRuleError(btcwire.RejectDuplicate,
+				return nil, txRuleError(btcwire.RejectDuplicate,
 					"transaction already exists")
 			}
 		}
 	}
 	delete(txStore, *txHash)
 
-	// Transaction is an orphan if any of the inputs don't exist.
+	// Transaction is an orphan if any of the referenced input transactions
+	// don't exist.  Adding orphans to the orphan pool is not handled by
+	// this function, and the caller should use maybeAddOrphan if this
+	// behavior is desired.
+	var missingParents []*btcwire.ShaHash
 	for _, txD := range txStore {
 		if txD.Err == btcdb.ErrTxShaMissing {
-			if isOrphan != nil {
-				*isOrphan = true
-			}
-			return nil
+			missingParents = append(missingParents, txD.Hash)
 		}
 	}
+	if len(missingParents) != 0 {
+		return missingParents, nil
+	}
 
 	// Perform several checks on the transaction inputs using the invariant
 	// rules in btcchain for what transactions are allowed into blocks.
@@ -924,9 +926,9 @@ func (mp *txMemPool) maybeAcceptTransaction(tx *btcutil.Tx, isOrphan *bool, isNe
 	txFee, err := btcchain.CheckTransactionInputs(tx, nextBlockHeight, txStore)
 	if err != nil {
 		if cerr, ok := err.(btcchain.RuleError); ok {
-			return chainRuleError(cerr)
+			return nil, chainRuleError(cerr)
 		}
-		return err
+		return nil, err
 	}
 
 	// Don't allow transactions with non-standard inputs if the network
@@ -943,7 +945,7 @@ func (mp *txMemPool) maybeAcceptTransaction(tx *btcutil.Tx, isOrphan *bool, isNe
 			}
 			str := fmt.Sprintf("transaction %v has a non-standard "+
 				"input: %v", txHash, err)
-			return txRuleError(rejectCode, str)
+			return nil, txRuleError(rejectCode, str)
 		}
 	}
 
@@ -959,15 +961,15 @@ func (mp *txMemPool) maybeAcceptTransaction(tx *btcutil.Tx, isOrphan *bool, isNe
 	numSigOps, err := btcchain.CountP2SHSigOps(tx, false, txStore)
 	if err != nil {
 		if cerr, ok := err.(btcchain.RuleError); ok {
-			return chainRuleError(cerr)
+			return nil, chainRuleError(cerr)
 		}
-		return err
+		return nil, err
 	}
 	numSigOps += btcchain.CountSigOps(tx)
 	if numSigOps > maxSigOpsPerTx {
 		str := fmt.Sprintf("transaction %v has too many sigops: %d > %d",
 			txHash, numSigOps, maxSigOpsPerTx)
-		return txRuleError(btcwire.RejectNonstandard, str)
+		return nil, txRuleError(btcwire.RejectNonstandard, str)
 	}
 
 	// Don't allow transactions with fees too low to get into a mined block.
@@ -987,7 +989,7 @@ func (mp *txMemPool) maybeAcceptTransaction(tx *btcutil.Tx, isOrphan *bool, isNe
 		str := fmt.Sprintf("transaction %v has %d fees which is under "+
 			"the required amount of %d", txHash, txFee,
 			minFee)
-		return txRuleError(btcwire.RejectInsufficientFee, str)
+		return nil, txRuleError(btcwire.RejectInsufficientFee, str)
 	}
 
 	// Free-to-relay transactions are rate limited here to prevent
@@ -1004,7 +1006,7 @@ func (mp *txMemPool) maybeAcceptTransaction(tx *btcutil.Tx, isOrphan *bool, isNe
 		if mp.pennyTotal >= cfg.FreeTxRelayLimit*10*1000 {
 			str := fmt.Sprintf("transaction %v has been rejected "+
 				"by the rate limiter due to low fees", txHash)
-			return txRuleError(btcwire.RejectInsufficientFee, str)
+			return nil, txRuleError(btcwire.RejectInsufficientFee, str)
 		}
 		oldTotal := mp.pennyTotal
 
@@ -1020,9 +1022,9 @@ func (mp *txMemPool) maybeAcceptTransaction(tx *btcutil.Tx, isOrphan *bool, isNe
 		standardScriptVerifyFlags)
 	if err != nil {
 		if cerr, ok := err.(btcchain.RuleError); ok {
-			return chainRuleError(cerr)
+			return nil, chainRuleError(cerr)
 		}
-		return err
+		return nil, err
 	}
 
 	// Add to transaction pool.
@@ -1040,29 +1042,33 @@ func (mp *txMemPool) maybeAcceptTransaction(tx *btcutil.Tx, isOrphan *bool, isNe
 		mp.server.rpcServer.gbtWorkState.NotifyMempoolTx(mp.lastUpdated)
 	}
 
-	return nil
+	return nil, nil
 }
 
 // MaybeAcceptTransaction is the main workhorse for handling insertion of new
 // free-standing transactions into a memory pool.  It includes functionality
 // such as rejecting duplicate transactions, ensuring transactions follow all
-// rules, orphan transaction handling, and insertion into the memory pool.  The
-// isOrphan parameter can be nil if the caller does not need to know whether
-// or not the transaction is an orphan.
+// rules, detecting orphan transactions, and insertion into the memory pool.
+//
+// If the transaction is an orphan (missing parent transactions), the
+// transaction is NOT added to the orphan pool, but each unknown referenced
+// parent is returned.  Use ProcessTransaction instead if new orphans should
+// be added to the orphan pool.
 //
 // This function is safe for concurrent access.
-func (mp *txMemPool) MaybeAcceptTransaction(tx *btcutil.Tx, isOrphan *bool, isNew, rateLimit bool) error {
+func (mp *txMemPool) MaybeAcceptTransaction(tx *btcutil.Tx, isNew, rateLimit bool) ([]*btcwire.ShaHash, error) {
 	// Protect concurrent access.
 	mp.Lock()
 	defer mp.Unlock()
 
-	return mp.maybeAcceptTransaction(tx, isOrphan, isNew, rateLimit)
+	return mp.maybeAcceptTransaction(tx, isNew, rateLimit)
 }
 
 // processOrphans determines if there are any orphans which depend on the passed
-// transaction hash (they are no longer orphans if true) and potentially accepts
-// them.  It repeats the process for the newly accepted transactions (to detect
-// further orphans which may no longer be orphans) until there are no more.
+// transaction hash (it is possible that they are no longer orphans) and
+// potentially accepts them to the memory pool.  It repeats the process for the
+// newly accepted transactions (to detect further orphans which may no longer be
+// orphans) until there are no more.
 //
 // This function MUST be called with the mempool lock held (for writes).
 func (mp *txMemPool) processOrphans(hash *btcwire.ShaHash) error {
@@ -1089,29 +1095,57 @@ func (mp *txMemPool) processOrphans(hash *btcwire.ShaHash) error {
 			enext = e.Next()
 			tx := e.Value.(*btcutil.Tx)
 
-			// Remove the orphan from the orphan pool.
+			// Remove the orphan from the orphan pool.  Current
+			// behavior requires that all saved orphans with
+			// a newly accepted parent are removed from the orphan
+			// pool and potentially added to the memory pool, but
+			// transactions which cannot be added to memory pool
+			// (including due to still being orphans) are expunged
+			// from the orphan pool.
+			//
+			// TODO(jrick): The above described behavior sounds
+			// like a bug, and I think we should investigate
+			// potentially moving orphans to the memory pool, but
+			// leaving them in the orphan pool if not all parent
+			// transactions are known yet.
 			orphanHash := tx.Sha()
 			mp.removeOrphan(orphanHash)
 
 			// Potentially accept the transaction into the
 			// transaction pool.
-			var isOrphan bool
-			err := mp.maybeAcceptTransaction(tx, &isOrphan, true, true)
+			missingParents, err := mp.maybeAcceptTransaction(tx,
+				true, true)
 			if err != nil {
 				return err
 			}
 
-			if !isOrphan {
-				// Generate the inventory vector and relay it.
+			if len(missingParents) == 0 {
+				// Generate and relay the inventory vector for the
+				// newly accepted transaction.
 				iv := btcwire.NewInvVect(btcwire.InvTypeTx, tx.Sha())
 				mp.server.RelayInventory(iv)
 			} else {
+				// Transaction is still an orphan.
+				// TODO(jrick): This removeOrphan call is
+				// likely unnecessary as it was unconditionally
+				// removed above and maybeAcceptTransaction won't
+				// add it back.
 				mp.removeOrphan(orphanHash)
 			}
 
 			// Add this transaction to the list of transactions to
 			// process so any orphans that depend on this one are
 			// handled too.
+			//
+			// TODO(jrick): In the case that this is still an orphan,
+			// we know that any other transactions in the orphan
+			// pool with this orphan as their parent are still
+			// orphans as well, and should be removed.  While
+			// recursively calling removeOrphan and
+			// maybeAcceptTransaction on these transactions is not
+			// wrong per se, it is overkill if all we care about is
+			// recursively removing child transactions of this
+			// orphan.
 			processHashes.PushBack(orphanHash)
 		}
 	}
@@ -1133,20 +1167,20 @@ func (mp *txMemPool) ProcessTransaction(tx *btcutil.Tx, allowOrphan, rateLimit b
 	txmpLog.Tracef("Processing transaction %v", tx.Sha())
 
 	// Potentially accept the transaction to the memory pool.
-	var isOrphan bool
-	err := mp.maybeAcceptTransaction(tx, &isOrphan, true, rateLimit)
+	missingParents, err := mp.maybeAcceptTransaction(tx, true, rateLimit)
 	if err != nil {
 		return err
 	}
 
-	if !isOrphan {
+	if len(missingParents) == 0 {
 		// Generate the inventory vector and relay it.
 		iv := btcwire.NewInvVect(btcwire.InvTypeTx, tx.Sha())
 		mp.server.RelayInventory(iv)
 
 		// Accept any orphan transactions that depend on this
-		// transaction (they are no longer orphans) and repeat for those
-		// accepted transactions until there are no more.
+		// transaction (they may no longer be orphans if all inputs
+		// are now available) and repeat for those accepted
+		// transactions until there are no more.
 		err := mp.processOrphans(tx.Sha())
 		if err != nil {
 			return err
@@ -1155,14 +1189,19 @@ func (mp *txMemPool) ProcessTransaction(tx *btcutil.Tx, allowOrphan, rateLimit b
 		// The transaction is an orphan (has inputs missing).  Reject
 		// it if the flag to allow orphans is not set.
 		if !allowOrphan {
+			// Only use the first missing parent transaction in
+			// the error message.
+			//
 			// NOTE: RejectDuplicate is really not an accurate
 			// reject code here, but it matches the reference
 			// implementation and there isn't a better choice due
 			// to the limited number of reject codes.  Missing
 			// inputs is assumed to mean they are already spent
 			// which is not really always the case.
-			return txRuleError(btcwire.RejectDuplicate,
-				"transaction spends unknown inputs")
+			str := fmt.Sprintf("orphan transaction %v references "+
+				"outputs of unknown or fully-spent "+
+				"transaction %v", tx.Sha(), missingParents[0])
+			return txRuleError(btcwire.RejectDuplicate, str)
 		}
 
 		// Potentially add the orphan transaction to the orphan pool.
```
