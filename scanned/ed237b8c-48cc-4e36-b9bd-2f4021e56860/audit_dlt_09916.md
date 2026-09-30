# [?] Merge pull request #587 from hyeonLewis/prevent-overflow

## Summary
Severity: Unknown
Chain: Kaia
Component: kaiachain/kaia
Published: 2025-10-16
Source: https://github.com/kaiachain/kaia/commit/9cfeed838c7f4c3db02e5e14180d9e5817f50206
Type: security-commit

## Details
Merge pull request #587 from hyeonLewis/prevent-overflow

blockchain/system: prevent overflow from uint64 to int64

## Patch
### blockchain/system/auction.go
```diff
@@ -55,12 +55,12 @@ func ReadGasBufferEstimate(backend bind.ContractCaller, contractAddr common.Addr
 func EncodeAuctionCallData(bid *auction.Bid) ([]byte, error) {
 	input := contracts.IAuctionEntryPointAuctionTx{
 		TargetTxHash:  bid.TargetTxHash,
-		BlockNumber:   big.NewInt(int64(bid.BlockNumber)),
+		BlockNumber:   new(big.Int).SetUint64(bid.BlockNumber),
 		Sender:        bid.Sender,
 		To:            bid.To,
-		Nonce:         big.NewInt(int64(bid.Nonce)),
+		Nonce:         new(big.Int).SetUint64(bid.Nonce),
 		Bid:           bid.Bid,
-		CallGasLimit:  big.NewInt(int64(bid.CallGasLimit)),
+		CallGasLimit:  new(big.Int).SetUint64(bid.CallGasLimit),
 		Data:          bid.Data,
 		SearcherSig:   bid.SearcherSig,
 		AuctioneerSig: bid.AuctioneerSig,
```
