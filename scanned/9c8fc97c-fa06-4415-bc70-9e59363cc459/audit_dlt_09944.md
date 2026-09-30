# [?] added constraints in CalcBaseFee to avoid zero divide panic

## Summary
Severity: Unknown
Chain: Kaia
Component: kaiachain/kaia
Published: 2022-06-14
Source: https://github.com/kaiachain/kaia/commit/abe98833ea477ac283fa1afcf47ba672ef950e51
Type: security-commit

## Details
added constraints in CalcBaseFee to avoid zero divide panic

## Patch
### consensus/misc/kip71.go
```diff
@@ -24,15 +24,21 @@ func VerifyKIP71Header(config *params.ChainConfig, parentHeader, header *types.H
 }
 
 func CalcBaseFee(parentHeader *types.Header, config *params.ChainConfig) *big.Int {
-	// If the current is the kip71 disabled block, then return default base fee (250ston)
-	if !config.IsKIP71ForkEnabled(parentHeader.Number) {
+	// If the parent is the kip71 disabled block or genesis, then return default base fee (250ston)
+	if !config.IsKIP71ForkEnabled(parentHeader.Number) || parentHeader.Number.Cmp(new(big.Int).SetUint64(0)) == 0 {
 		return new(big.Int).SetUint64(config.UnitPrice)
 	}
 
 	// governance parameters
 	lowerBoundBaseFee := new(big.Int).SetUint64(config.Governance.KIP71.LowerBoundBaseFee)
 	upperBoundBaseFee := new(big.Int).SetUint64(config.Governance.KIP71.UpperBoundBaseFee)
-	baseFeeDenominator := new(big.Int).SetUint64(config.Governance.KIP71.BaseFeeDenominator)
+	var baseFeeDenominator *big.Int
+	if config.Governance.KIP71.BaseFeeDenominator == 0 {
+		// To avoid panic, set the fluctuation range small
+		baseFeeDenominator = new(big.Int).SetUint64(64)
+	} else {
+		baseFeeDenominator = new(big.Int).SetUint64(config.Governance.KIP71.BaseFeeDenominator)
+	}
 	gasTarget := config.Governance.KIP71.GasTarget
 	upperGasLimit := config.Governance.KIP71.MaxBlockGasUsedForBaseFee
 
```
