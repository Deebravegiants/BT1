# [?] Fix underflow inside the gas charging hook (#3688)

## Summary
Severity: Unknown
Chain: Arbitrum
Component: OffchainLabs/nitro
Published: 2025-09-24
Source: https://github.com/OffchainLabs/nitro/commit/60ba39afe72c1e03870aa4276e5a4d21c9fccc5f
Type: security-commit

## Details
Fix underflow inside the gas charging hook (#3688)

## Patch
### arbos/tx_processor.go
```diff
@@ -496,7 +496,7 @@ func (p *TxProcessor) GasChargingHook(gasRemaining *uint64, intrinsicGas uint64)
 				return tipReceipient, multigas.ZeroGas(), err
 			}
 			// Reduce the max by intrinsicGas because it was already charged
-			max -= intrinsicGas
+			max = arbmath.SaturatingUSub(max, intrinsicGas)
 		}
 		if *gasRemaining > max {
 			p.computeHoldGas = *gasRemaining - max
```
