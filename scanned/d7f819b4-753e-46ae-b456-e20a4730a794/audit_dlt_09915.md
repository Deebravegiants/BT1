# [?] Avoid unexpected panic when nil is given to CalcBlobFee

## Summary
Severity: Unknown
Chain: Kaia
Component: kaiachain/kaia
Published: 2025-12-18
Source: https://github.com/kaiachain/kaia/commit/e454dc045d1d35c22e0eaf319159b8eef5da5417
Type: security-commit

## Details
Avoid unexpected panic when nil is given to CalcBlobFee

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
