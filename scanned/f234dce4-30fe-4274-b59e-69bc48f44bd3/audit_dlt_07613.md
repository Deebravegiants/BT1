# [?] miner: avoid data race in miner (#24349)

## Summary
Severity: Unknown
Chain: Ethereum
Component: ethereum/go-ethereum
Published: 2022-02-07
Source: https://github.com/ethereum/go-ethereum/commit/2d20fed893faa894f50af709349b13b6ad9b45db
Type: security-commit

## Details
miner: avoid data race in miner (#24349)

## Patch
### miner/worker.go
```diff
@@ -1134,6 +1134,9 @@ func (w *worker) commit(env *environment, interval func(), update bool, start ti
 		if interval != nil {
 			interval()
 		}
+		// Create a local environment copy, avoid the data race with snapshot state.
+		// https://github.com/ethereum/go-ethereum/issues/24299
+		env := env.copy()
 		block, err := w.engine.FinalizeAndAssemble(w.chain, env.header, env.state, env.txs, env.unclelist(), env.receipts)
 		if err != nil {
 			return err
```
