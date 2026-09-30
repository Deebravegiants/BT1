# [?] Fix panic when fetching the pending block state over RPC (#1769)

## Summary
Severity: Unknown
Chain: Celo
Component: celo-org/celo-blockchain
Published: 2022-01-19
Source: https://github.com/celo-org/celo-blockchain/commit/c3aba4ec747fc1cbf660e4c46db9e3b2b36bcdf5
Type: security-commit

## Details
Fix panic when fetching the pending block state over RPC (#1769)

## Patch
### eth/api_backend.go
```diff
@@ -142,6 +142,9 @@ func (b *EthAPIBackend) StateAndHeaderByNumber(ctx context.Context, number rpc.B
 	// Pending state is only known by the miner
 	if number == rpc.PendingBlockNumber {
 		block, state := b.eth.miner.Pending()
+		if block == nil && state == nil {
+			return nil, nil, errors.New("no pending block")
+		}
 		return state, block.Header(), nil
 	}
 	// Otherwise resolve the block number and return its state
```
