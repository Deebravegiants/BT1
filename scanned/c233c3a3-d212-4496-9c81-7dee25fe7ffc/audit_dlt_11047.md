# [?] Avoid underflow in state transition

## Summary
Severity: Unknown
Chain: Arbitrum
Component: OffchainLabs/go-ethereum
Published: 2026-03-20
Source: https://github.com/OffchainLabs/go-ethereum/commit/ae7ed10bd1a1156264930e29f92a906fe00f044b
Type: security-commit

## Details
Avoid underflow in state transition

## Patch
### core/state_transition.go
```diff
@@ -784,6 +784,7 @@ func (st *stateTransition) execute() (*ExecutionResult, error) {
 		effectiveTip = new(big.Int).Sub(msg.GasPrice, st.evm.Context.BaseFee)
 	}
 	effectiveTipU256, _ := uint256.FromBig(effectiveTip)
+	gasUsed := st.gasUsed()
 
 	if st.evm.Config.NoBaseFee && msg.GasFeeCap.Sign() == 0 && msg.GasTipCap.Sign() == 0 {
 		// Skip fee payment when NoBaseFee is set and the fee fields
@@ -792,7 +793,10 @@ func (st *stateTransition) execute() (*ExecutionResult, error) {
 	} else {
 		// Only charge the tip on compute gas, not poster gas.
 		// The poster is compensated separately in EndTxHook.
-		computeGasUsed := st.gasUsed() - st.evm.ProcessingHook.PosterGas()
+		computeGasUsed, posterGas := uint64(0), st.evm.ProcessingHook.PosterGas()
+		if gasUsed > posterGas {
+			computeGasUsed = gasUsed - posterGas
+		}
 		fee := new(uint256.Int).SetUint64(computeGasUsed)
 		fee.Mul(fee, effectiveTipU256)
 		st.state.AddBalance(tipReceipient, fee, tracing.BalanceIncreaseRewardTransactionFee)
@@ -820,7 +824,7 @@ func (st *stateTransition) execute() (*ExecutionResult, error) {
 	}
 
 	return &ExecutionResult{
-		UsedGas:          st.gasUsed(),
+		UsedGas:          gasUsed,
 		MaxUsedGas:       peakGasUsed,
 		Err:              vmerr,
 		ReturnData:       ret,
```
