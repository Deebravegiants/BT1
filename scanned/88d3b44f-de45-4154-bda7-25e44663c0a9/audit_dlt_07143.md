# [?] cmd/puppeth: fix panic error when export aleth genesis wo/ precompile-addresses (#18344)

## Summary
Severity: Unknown
Chain: Celo
Component: celo-org/celo-blockchain
Published: 2019-01-04
Source: https://github.com/celo-org/celo-blockchain/commit/3f421aca54bb5216e0f949966481fa4516c52273
Type: security-commit

## Details
cmd/puppeth: fix panic error when export aleth genesis wo/ precompile-addresses (#18344)

* cmd/puppeth: fix panic error when export aleth genesis wo/ precompile-addresses

* cmd/puppeth: don't need to handle duplicate set

## Patch
### cmd/puppeth/genesis.go
```diff
@@ -174,7 +174,11 @@ func (spec *alethGenesisSpec) setPrecompile(address byte, data *alethGenesisSpec
 	if spec.Accounts == nil {
 		spec.Accounts = make(map[common.UnprefixedAddress]*alethGenesisSpecAccount)
 	}
-	spec.Accounts[common.UnprefixedAddress(common.BytesToAddress([]byte{address}))].Precompiled = data
+	addr := common.UnprefixedAddress(common.BytesToAddress([]byte{address}))
+	if _, exist := spec.Accounts[addr]; !exist {
+		spec.Accounts[addr] = &alethGenesisSpecAccount{}
+	}
+	spec.Accounts[addr].Precompiled = data
 }
 
 func (spec *alethGenesisSpec) setAccount(address common.Address, account core.GenesisAccount) {
```
