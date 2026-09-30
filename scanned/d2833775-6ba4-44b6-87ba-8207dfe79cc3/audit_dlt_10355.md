# [?] fix race condition and overflow in MaxGasLimit

## Summary
Severity: Unknown
Chain: Sonic
Component: 0xsoniclabs/sonic
Published: 2021-01-26
Source: https://github.com/0xsoniclabs/sonic/commit/dd3d223066cca59a3a97a45cd4d04a5138f6b787
Type: security-commit

## Details
fix race condition and overflow in MaxGasLimit

## Patch
### gossip/evm_state_reader.go
```diff
@@ -31,7 +31,11 @@ func (r *EvmStateReader) MinGasPrice() *big.Int {
 }
 
 func (r *EvmStateReader) MaxGasLimit() uint64 {
-	return (r.store.GetRules().Economy.Gas.MaxEventGas - r.store.GetRules().Economy.Gas.EventGas) * 2 / 3
+	rules := r.store.GetRules()
+	if rules.Economy.Gas.MaxEventGas < rules.Economy.Gas.EventGas {
+		return 0
+	}
+	return (rules.Economy.Gas.MaxEventGas - rules.Economy.Gas.EventGas) * 2 / 3
 }
 
 func (r *EvmStateReader) CurrentBlock() *evmcore.EvmBlock {
```
