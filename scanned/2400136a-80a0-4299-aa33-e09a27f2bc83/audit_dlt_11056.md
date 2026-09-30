# [?] Fix DeserializeHeaderExtraInformation that panics for nil header

## Summary
Severity: Unknown
Chain: Arbitrum
Component: OffchainLabs/go-ethereum
Published: 2023-09-26
Source: https://github.com/OffchainLabs/go-ethereum/commit/45efc8230c2561cf56652dabccdd670101f75b0c
Type: security-commit

## Details
Fix DeserializeHeaderExtraInformation that panics for nil header

## Patch
### core/types/arb_types.go
```diff
@@ -504,7 +504,7 @@ func (info HeaderInfo) UpdateHeaderWithInfo(header *Header) {
 }
 
 func DeserializeHeaderExtraInformation(header *Header) HeaderInfo {
-	if header.BaseFee == nil || header.BaseFee.Sign() == 0 || len(header.Extra) != 32 || header.Difficulty.Cmp(common.Big1) != 0 {
+	if header == nil || header.BaseFee == nil || header.BaseFee.Sign() == 0 || len(header.Extra) != 32 || header.Difficulty.Cmp(common.Big1) != 0 {
 		// imported blocks have no base fee
 		// The genesis block doesn't have an ArbOS encoded extra field
 		return HeaderInfo{}
```
