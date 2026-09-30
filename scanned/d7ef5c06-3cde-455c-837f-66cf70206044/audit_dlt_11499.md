# [?] fix: underflow issue

## Summary
Severity: Unknown
Chain: Oracle
Component: pyth-network/pyth-crosschain
Published: 2023-09-04
Source: https://github.com/pyth-network/pyth-crosschain/commit/7cbdcb562d3896d75c59902887629a57c14c95e0
Type: security-commit

## Details
fix: underflow issue

## Patch
### target_chains/ethereum/examples/oracle_swap/contract/src/OracleSwap.sol
```diff
@@ -101,7 +101,7 @@ contract OracleSwap {
 
         uint8 priceDecimals = uint8(uint32(-1 * price.expo));
 
-        if (targetDecimals - priceDecimals >= 0) {
+        if (targetDecimals >= priceDecimals) {
             return
                 uint(uint64(price.price)) *
                 10 ** uint32(targetDecimals - priceDecimals);
```
