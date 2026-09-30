# [?] tests/fuzzers/les: fix crash in fuzzer (#28362)

## Summary
Severity: Unknown
Chain: Ethereum
Component: ethereum/go-ethereum
Published: 2023-10-17
Source: https://github.com/ethereum/go-ethereum/commit/d782dc2341004233d7809c40e37509f06fbc2c1c
Type: security-commit

## Details
tests/fuzzers/les: fix crash in fuzzer (#28362)

## Patch
### tests/fuzzers/les/les-fuzzer.go
```diff
@@ -70,7 +70,7 @@ func makechain() (bc *core.BlockChain, addresses []common.Address, txHashes []co
 			)
 			nonce := uint64(i)
 			if i%4 == 0 {
-				tx, _ = types.SignTx(types.NewContractCreation(nonce, big.NewInt(0), 200000, big.NewInt(0), testContractCode), signer, bankKey)
+				tx, _ = types.SignTx(types.NewContractCreation(nonce, big.NewInt(0), 200000, big.NewInt(params.GWei), testContractCode), signer, bankKey)
 				addr = crypto.CreateAddress(bankAddr, nonce)
 			} else {
 				addr = common.BigToAddress(big.NewInt(int64(i)))
```
