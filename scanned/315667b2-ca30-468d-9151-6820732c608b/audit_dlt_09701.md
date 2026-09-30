# [?] core: gaDeriveHash: only set balance if non-nil, avoid panic

## Summary
Severity: Unknown
Chain: Ethereum Classic
Component: etclabscore/core-geth
Published: 2024-02-28
Source: https://github.com/etclabscore/core-geth/commit/ec2e6a7ab5f24c1380bc5d4b43e99ea78106a903
Type: security-commit

## Details
core: gaDeriveHash: only set balance if non-nil, avoid panic

Date: 2024-02-28 06:52:20-07:00
Signed-off-by: meows <b5c6@protonmail.com>

## Patch
### core/genesis.go
```diff
@@ -370,7 +370,9 @@ func gaDeriveHash(ga *genesisT.GenesisAlloc) (common.Hash, error) {
 		return common.Hash{}, err
 	}
 	for addr, account := range *ga {
-		statedb.AddBalance(addr, uint256.MustFromBig(account.Balance))
+		if account.Balance != nil {
+			statedb.AddBalance(addr, uint256.MustFromBig(account.Balance))
+		}
 		statedb.SetCode(addr, account.Code)
 		statedb.SetNonce(addr, account.Nonce)
 		for key, value := range account.Storage {
```
