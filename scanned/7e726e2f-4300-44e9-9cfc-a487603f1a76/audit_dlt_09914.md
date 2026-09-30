# [?] Merge pull request #689 from Mdaiki0730/feat/avoid-calcblobfee-panic

## Summary
Severity: Unknown
Chain: Kaia
Component: kaiachain/kaia
Published: 2025-12-18
Source: https://github.com/kaiachain/kaia/commit/c508c4254d86f01f81da5e79e0b6b305bd767840
Type: security-commit

## Details
Merge pull request #689 from Mdaiki0730/feat/avoid-calcblobfee-panic

kip279: Avoid unexpected panic when nil is given to CalcBlobFee

## Patch
### blockchain/evm.go
```diff
@@ -68,7 +68,9 @@ func NewEVMBlockContext(header *types.Header, chain ChainContext, author *common
 	}
 
 	if header.ExcessBlobGas != nil {
-		blobBaseFee = eip4844.CalcBlobFee(header.BaseFee)
+		// Since CalcBlobFee returns nil for a nil baseFee,
+		// use baseFee instead of header.BaseFee to at least force blobBaseFee to zero in this context.
+		blobBaseFee = eip4844.CalcBlobFee(baseFee)
 	} else { // Before Osaka hardfork, BLOBBASEFEE (4a) returns 0
 		blobBaseFee = new(big.Int).SetUint64(params.ZeroBaseFee)
 	}
```

### consensus/misc/eip4844/eip4844.go
```diff
@@ -178,6 +178,11 @@ func calcExcessBlobGas(isOsaka bool, bcfg *BlobConfig, parent *types.Header) uin
 
 // CalcBlobFee calculates the blobfee for KIP-279 from the header's base fee field.
 func CalcBlobFee(baseFee *big.Int) *big.Int {
+	// If baseFee is nil, CalcBlobFee will return nil as it cannot be calculated.
+	// Returning nil makes the difference from 0 explicit.
+	if baseFee == nil {
+		return nil
+	}
 	return new(big.Int).Mul(baseFee, new(big.Int).SetUint64(params.BlobBaseFeeMultiplier))
 }
 
```
