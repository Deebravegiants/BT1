# [?] accounts/abi/bind/backends: fix race condition in simulated backend (#23898)

## Summary
Severity: Unknown
Chain: Ethereum
Component: ethereum/go-ethereum
Published: 2021-11-12
Source: https://github.com/ethereum/go-ethereum/commit/abc74a5ffeb7e211954178e5d7b8543d5bd3d3cc
Type: security-commit

## Details
accounts/abi/bind/backends: fix race condition in simulated backend (#23898)

Now that `SimulatedBackend.SuggestGasPrice` inspects member values, a lock needs to be added to prevent a race condition.

## Patch
### accounts/abi/bind/backends/simulated.go
```diff
@@ -462,6 +462,9 @@ func (b *SimulatedBackend) PendingNonceAt(ctx context.Context, account common.Ad
 // SuggestGasPrice implements ContractTransactor.SuggestGasPrice. Since the simulated
 // chain doesn't have miners, we just return a gas price of 1 for any call.
 func (b *SimulatedBackend) SuggestGasPrice(ctx context.Context) (*big.Int, error) {
+	b.mu.Lock()
+	defer b.mu.Unlock()
+
 	if b.pendingBlock.Header().BaseFee != nil {
 		return b.pendingBlock.Header().BaseFee, nil
 	}
```
