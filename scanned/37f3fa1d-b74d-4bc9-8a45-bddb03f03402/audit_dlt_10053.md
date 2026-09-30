# [?] fix panic

## Summary
Severity: Unknown
Chain: MultiversX
Component: multiversx/mx-chain-go
Published: 2025-10-28
Source: https://github.com/multiversx/mx-chain-go/commit/9715c7d9f9c9944eddfc7de03a44c9c0ac9075e4
Type: security-commit

## Details
fix panic

## Patch
### process/block/preprocess/transactions.go
```diff
@@ -133,6 +133,7 @@ func NewTransactionPreprocessor(
 		accountsProposal:           args.AccountsProposal,
 		pubkeyConverter:            args.PubkeyConverter,
 		enableEpochsHandler:        args.EnableEpochsHandler,
+		enableRoundsHandler:        args.EnableRoundsHandler,
 		processedMiniBlocksTracker: args.ProcessedMiniBlocksTracker,
 		txExecutionOrderHandler:    args.TxExecutionOrderHandler,
 	}
```
