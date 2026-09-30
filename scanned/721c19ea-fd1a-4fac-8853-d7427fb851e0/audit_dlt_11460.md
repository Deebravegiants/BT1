# [?] fix: solana race condition + logging (#9001)

## Summary
Severity: Unknown
Chain: Bridge
Component: smartcontractkit/ccip
Published: 2023-04-21
Source: https://github.com/smartcontractkit/ccip/commit/b57ab7566f30ad09ed2542306791300bb8be5bd5
Type: security-commit

## Details
fix: solana race condition + logging (#9001)

* fix: solana race condition + logging

* lint fix

## Patch
### core/chains/solana/soltxm/txm.go
```diff
@@ -204,8 +204,8 @@ func (txm *Txm) sendWithRetry(chanCtx context.Context, baseTx solanaGo.Transacti
 		return solanaGo.Transaction{}, uuid.Nil, solanaGo.Signature{}, errors.Wrap(initSendErr, "tx failed initial transmit")
 	}
 
-	var sigsLock sync.RWMutex
-	sigs := []solanaGo.Signature{sig}
+	var sigs signatureList
+	sigs.Append(sig) // add initial signature
 
 	// store tx signature + cancel function
 	id, initStoreErr := txm.txs.New(sig, cancel)
@@ -226,7 +226,7 @@ func (txm *Txm) sendWithRetry(chanCtx context.Context, baseTx solanaGo.Transacti
 			select {
 			case <-ctx.Done():
 				// stop sending tx after retry tx ctx times out (does not stop confirmation polling for tx)
-				txm.lggr.Debugw("stopped tx retry", "id", id, "signatures", sigs)
+				txm.lggr.Debugw("stopped tx retry", "id", id, "signatures", sigs.List())
 				return
 			case <-tick:
 				var shouldBump bool
@@ -249,13 +249,16 @@ func (txm *Txm) sendWithRetry(chanCtx context.Context, baseTx solanaGo.Transacti
 
 				// take currentTx and broadcast, if bumped fee -> save signature to list
 				go func(bump bool, count uint, retryTx solanaGo.Transaction) {
+					// calculate index to compare before broadcasting
+					index := sigs.Length() - 1
+
 					retrySig, retrySendErr := client.SendTx(ctx, &retryTx)
 					// this could occur if endpoint goes down or if ctx cancelled
 					if retrySendErr != nil {
 						if strings.Contains(retrySendErr.Error(), "context canceled") || strings.Contains(retrySendErr.Error(), "context deadline exceeded") {
-							txm.lggr.Debugw("ctx error on send retry transaction", "error", retrySendErr, "signatures", sigs, "id", id)
+							txm.lggr.Debugw("ctx error on send retry transaction", "error", retrySendErr, "signatures", sigs.List(), "id", id)
 						} else {
-							txm.lggr.Warnw("failed to send retry transaction", "error", retrySendErr, "signatures", sigs, "id", id)
+							txm.lggr.Warnw("failed to send retry transaction", "error", retrySendErr, "signatures", sigs.List(), "id", id)
 						}
 						return
 					}
@@ -266,18 +269,15 @@ func (txm *Txm) sendWithRetry(chanCtx context.Context, baseTx solanaGo.Transacti
 							txm.lggr.Warnw("error in adding retry transaction", "error", retryStoreErr, "id", id)
 							return
 						}
-						sigsLock.Lock()
-						sigs = append(sigs, retrySig)
-						sigsLock.Unlock()
-						txm.lggr.Debugw("tx rebroadcast with bumped fee", "id", id, "fee", getFee(count), "signatures", sigs)
+						sigsList, sigsLength := sigs.Append(retrySig)
+						index = sigsLength - 1
+						txm.lggr.Debugw("tx rebroadcast with bumped fee", "id", id, "fee", getFee(count), "signatures", sigsList)
 					}
 
 					// this should never happen (should match the last signature saved to sigs)
-					sigsLock.RLock()
-					if len(sigs) == 0 || retrySig != sigs[len(sigs)-1] {
-						txm.lggr.Criticalw("original signature does not match retry signature", "expectedSignatures", sigs, "receivedSignature", retrySig)
+					if fetchedSig, fetchErr := sigs.Get(index); fetchErr != nil || retrySig != fetchedSig {
+						txm.lggr.Errorw("original signature does not match retry signature", "expectedSignatures", sigs.List(), "receivedSignature", retrySig, "error", fetchErr)
 					}
-					sigsLock.RUnlock()
 				}(shouldBump, bumpCount, currentTx)
 			}
 
@@ -347,15 +347,15 @@ func (txm *Txm) confirm(ctx context.Context) {
 						// check confirm timeout exceeded
 						if txm.txs.Expired(s[i], txm.cfg.TxConfirmTimeout()) {
 							id := txm.txs.OnError(s[i], TxFailDrop)
-							txm.lggr.Warnw("failed to find transaction within confirm timeout", "id", id, "signature", s[i], "timeoutSeconds", txm.cfg.TxConfirmTimeout())
+							txm.lggr.Infow("failed to find transaction within confirm timeout", "id", id, "signature", s[i], "timeoutSeconds", txm.cfg.TxConfirmTimeout())
 						}
 						continue
 					}
 
 					// if signature has an error, end polling
 					if res[i].Err != nil {
 						id := txm.txs.OnError(s[i], TxFailRevert)
-						txm.lggr.Errorw("tx state: failed",
+						txm.lggr.Debugw("tx state: failed",
 							"id", id,
 							"signature", s[i],
 							"error", res[i].Err,
@@ -373,7 +373,7 @@ func (txm *Txm) confirm(ctx context.Context) {
 						// check confirm timeout exceeded
 						if txm.txs.Expired(s[i], txm.cfg.TxConfirmTimeout()) {
 							id := txm.txs.OnError(s[i], TxFailDrop)
-							txm.lggr.Warnw("tx failed to move beyond 'processed' within confirm timeout", "id", id, "signature", s[i], "timeoutSeconds", txm.cfg.TxConfirmTimeout())
+							txm.lggr.Debugw("tx failed to move beyond 'processed' within confirm timeout", "id", id, "signature", s[i], "timeoutSeconds", txm.cfg.TxConfirmTimeout())
 						}
 						continue
 					}
@@ -438,7 +438,7 @@ func (txm *Txm) simulate(ctx context.Context) {
 			if err != nil {
 				// this error can occur if endpoint goes down or if invalid signature (invalid signature should occur further upstream in sendWithRetry)
 				// allow retry to continue in case temporary endpoint failure (if still invalid, confirm or timeout will cleanup)
-				txm.lggr.Errorw("failed to simulate tx", "id", msg.id, "signature", msg.signature, "error", err)
+				txm.lggr.Debugw("failed to simulate tx", "id", msg.id, "signature", msg.signature, "error", err)
 				continue
 			}
 
@@ -455,12 +455,12 @@ func (txm *Txm) simulate(ctx context.Context) {
 			// blockhash not found when simulating, occurs when network bank has not seen the given blockhash or tx is too old
 			// let confirmation process clean up
 			case strings.Contains(errStr, "BlockhashNotFound"):
-				txm.lggr.Warnw("simulate: BlockhashNotFound", "id", msg.id, "signature", msg.signature, "result", res)
+				txm.lggr.Debugw("simulate: BlockhashNotFound", "id", msg.id, "signature", msg.signature, "result", res)
 				continue
 			// transaction will encounter execution error/revert, mark as reverted to remove from confirmation + retry
 			case strings.Contains(errStr, "InstructionError"):
 				txm.txs.OnError(msg.signature, TxFailSimRevert) // cancel retry
-				txm.lggr.Warnw("simulate: InstructionError", "id", msg.id, "signature", msg.signature, "result", res)
+				txm.lggr.Debugw("simulate: InstructionError", "id", msg.id, "signature", msg.signature, "result", res)
 				continue
 			// transaction is already processed in the chain, letting txm confirmation handle
 			case strings.Contains(errStr, "AlreadyProcessed"):
@@ -469,7 +469,7 @@ func (txm *Txm) simulate(ctx context.Context) {
 			// unrecognized errors (indicates more concerning failures)
 			default:
 				txm.txs.OnError(msg.signature, TxFailSimOther) // cancel retry
-				txm.lggr.Errorw("simulate: unrecognized error", "id", msg.id, "signature", msg.signature, "result", res)
+				txm.lggr.Warnw("simulate: unrecognized error", "id", msg.id, "signature", msg.signature, "result", res)
 				continue
 			}
 		}
```

### core/chains/solana/soltxm/utils.go
```diff
@@ -1,8 +1,10 @@
 package soltxm
 
 import (
+	"errors"
 	"fmt"
 	"sort"
+	"sync"
 
 	"github.com/gagliardetto/solana-go"
 	"github.com/gagliardetto/solana-go/rpc"
@@ -69,3 +71,37 @@ func convertStatus(res *rpc.SignatureStatusesResult) uint {
 
 	return NotFound
 }
+
+type signatureList struct {
+	sigs []solana.Signature
+	lock sync.RWMutex
+}
+
+func (s *signatureList) Get(index int) (sig solana.Signature, err error) {
+	s.lock.RLock()
+	defer s.lock.RUnlock()
+	if index >= len(s.sigs) {
+		return sig, errors.New("invalid index")
+	}
+	return s.sigs[index], nil
+}
+
+func (s *signatureList) List() []solana.Signature {
+	s.lock.RLock()
+	defer s.lock.RUnlock()
+	return s.sigs
+}
+
+func (s *signatureList) Length() int {
+	s.lock.RLock()
+	defer s.lock.RUnlock()
+	return len(s.sigs)
+}
+
+func (s *signatureList) Append(sig solana.Signature) (sigs []solana.Signature, count int) {
+	s.lock.Lock()
+	defer s.lock.Unlock()
+
+	s.sigs = append(s.sigs, sig)
+	return s.sigs, len(s.sigs)
+}
```
