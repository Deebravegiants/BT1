# [?] Merge pull request from GHSA-ghr9-hwq8-5h7f

## Summary
Severity: Unknown
Chain: Kaia
Component: kaiachain/kaia
Published: 2023-07-26
Source: https://github.com/kaiachain/kaia/commit/d5f24d573d3ca0e68614f7224101d8cf99fa5a2a
Type: security-commit

## Details
Merge pull request from GHSA-ghr9-hwq8-5h7f

Fix logic bug in contract creation

## Patch
### blockchain/vm/evm.go
```diff
@@ -453,7 +453,9 @@ func (evm *EVM) create(caller types.ContractRef, codeAndHash *codeAndHash, gas u
 		evm.StateDB.AddAddressToAccessList(address)
 	}
 
-	if evm.StateDB.Exist(address) {
+	// Ensure there's no existing contract already at the designated address
+	contractHash := evm.StateDB.GetCodeHash(address)
+	if evm.StateDB.GetNonce(address) != 0 || (contractHash != (common.Hash{}) && contractHash != emptyCodeHash) {
 		return nil, common.Address{}, 0, ErrContractAddressCollision // TODO-Klaytn-Issue615
 	}
 	if common.IsPrecompiledContractAddress(address) {
```
