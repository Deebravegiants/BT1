# [?] (fixup) change to overflow intead of using MaxUint64

## Summary
Severity: Unknown
Chain: Kaia
Component: kaiachain/kaia
Published: 2025-05-08
Source: https://github.com/kaiachain/kaia/commit/768bdb9840620757864b3f502e14fdd9d7f9f27e
Type: security-commit

## Details
(fixup) change to overflow intead of using MaxUint64

## Patch
### blockchain/state_transition.go
```diff
@@ -283,18 +283,19 @@ func (st *StateTransition) preCheck() error {
 
 	// Make sure this transaction's nonce is correct.
 	if st.msg.CheckNonce() {
-		nonce := st.state.GetNonce(st.msg.ValidatedSender())
-		if nonce < st.msg.Nonce() {
+		stNonce := st.state.GetNonce(st.msg.ValidatedSender())
+		txNonce := st.msg.Nonce()
+		if stNonce < txNonce {
 			logger.Debug(ErrNonceTooHigh.Error(), "account", st.msg.ValidatedSender().String(),
-				"accountNonce", nonce, "txNonce", st.msg.Nonce(), "txHash", st.msg.Hash().String())
+				"accountNonce", stNonce, "txNonce", txNonce, "txHash", st.msg.Hash().String())
 			return ErrNonceTooHigh
-		} else if nonce > st.msg.Nonce() {
+		} else if stNonce > txNonce {
 			logger.Debug(ErrNonceTooLow.Error(), "account", st.msg.ValidatedSender().String(),
-				"accountNonce", nonce, "txNonce", st.msg.Nonce(), "txHash", st.msg.Hash().String())
+				"accountNonce", stNonce, "txNonce", txNonce, "txHash", st.msg.Hash().String())
 			return ErrNonceTooLow
-		} else if st.msg.Nonce() > math.MaxUint64-1 {
+		} else if stNonce+1 < stNonce {
 			return fmt.Errorf("%w: address %v, nonce: %d", ErrNonceMax,
-				st.msg.ValidatedSender().Hex(), st.msg.Nonce())
+				st.msg.ValidatedSender().Hex(), stNonce)
 		}
 	}
 
```
