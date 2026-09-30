# [?] Return custom error to avoid nil pointer panic

## Summary
Severity: Unknown
Chain: Kaia
Component: kaiachain/kaia
Published: 2025-03-31
Source: https://github.com/kaiachain/kaia/commit/802e6b3963ddbb9405e7d1eaea0ec7eefe0c389e
Type: security-commit

## Details
Return custom error to avoid nil pointer panic

## Patch
### kerrors/kerrors.go
```diff
@@ -56,7 +56,8 @@ var (
 	ErrNestedCompositeType                  = errors.New("nested composite type")
 	ErrLegacyTransactionMustBeWithLegacyKey = errors.New("a legacy transaction must be with a legacy account key")
 
-	ErrDeprecated   = errors.New("deprecated feature")
-	ErrNotSupported = errors.New("not supported")
+	ErrDeprecated            = errors.New("deprecated feature")
+	ErrNotSupported          = errors.New("not supported")
 	ErrRevertedBundleByVmErr = errors.New("bundle is reverted by vm err")
+	ErrTxGeneration          = errors.New("transaction generation failed")
 )
```

### work/worker.go
```diff
@@ -795,7 +795,7 @@ CommitTransactionLoop:
 		if len(targetBundle.BundleTxs) != 0 {
 			atomic.StoreInt32(&isExecutingBundleTxs, 1)
 			err, tx, logs = env.commitBundleTransaction(targetBundle, bc, rewardbase, vmConfig)
-			if err != nil {
+			if err != nil && tx != nil {
 				// override sender to error tx
 				from, _ = types.Sender(env.signer, tx)
 			}
@@ -844,6 +844,11 @@ CommitTransactionLoop:
 			logger.Trace("Skipping transaction in bundle reverted by vm err", "sender", from, "hash", tx.Hash().String())
 			builder_impl.PopTxs(&incorporatedTxs, numShift, &bundles, env.signer)
 
+		case kerrors.ErrTxGeneration:
+			// Pop transaction in bundle due to tx generation error without shifting in the next from the account
+			logger.Trace("Skipping transaction in bundle due to tx generation error", "err", err)
+			builder_impl.PopTxs(&incorporatedTxs, numShift, &bundles, env.signer)
+
 		case nil:
 			// Everything ok, collect the logs and shift in the next transaction from the same account
 			coalescedLogs = append(coalescedLogs, logs...)
@@ -916,7 +921,7 @@ func (env *Task) commitBundleTransaction(bundle *builder.Bundle, bc BlockChain,
 				*env.state = *lastSnapshot
 				env.header.GasUsed = gasUsedSnapshot
 				env.tcount = tcountSnapshot
-				return err, &types.Transaction{}, nil
+				return kerrors.ErrTxGeneration, nil, nil
 			}
 		} else {
 			tx = txOrGen.(*types.Transaction)
@@ -941,7 +946,7 @@ func (env *Task) commitBundleTransaction(bundle *builder.Bundle, bc BlockChain,
 			if err == nil {
 				err = kerrors.ErrRevertedBundleByVmErr
 			}
-			return err, tx, nil
+			return err, nil, nil
 		}
 
 		env.tcount++
@@ -953,7 +958,7 @@ func (env *Task) commitBundleTransaction(bundle *builder.Bundle, bc BlockChain,
 	env.txs = append(env.txs, txs...)
 	env.receipts = append(env.receipts, receipts...)
 
-	return nil, &types.Transaction{}, logs
+	return nil, nil, logs
 }
 
 func NewTask(config *params.ChainConfig, signer types.Signer, statedb *state.StateDB, header *types.Header) *Task {
```
