# [?] Merge pull request #174 from mdehoog/michael/fix-superchain-panic

## Summary
Severity: Unknown
Chain: Optimism
Component: ethereum-optimism/op-geth
Published: 2023-10-27
Source: https://github.com/ethereum-optimism/op-geth/commit/237170bc3d03cea588b4f671cae55b65b4d51877
Type: security-commit

## Details
Merge pull request #174 from mdehoog/michael/fix-superchain-panic

Fix potential nil pointer dereference panic in superchain overrides

## Patch
### core/genesis.go
```diff
@@ -286,7 +286,7 @@ func SetupGenesisBlockWithOverride(db ethdb.Database, triedb *trie.Database, gen
 		if config != nil {
 			// If applying the superchain-registry to a known OP-Stack chain,
 			// then override the local chain-config with that from the registry.
-			if overrides != nil && overrides.ApplySuperchainUpgrades && config.IsOptimism() && config.ChainID != nil && genesis.Config.ChainID.IsUint64() {
+			if overrides != nil && overrides.ApplySuperchainUpgrades && config.IsOptimism() && config.ChainID != nil && config.ChainID.IsUint64() {
 				if _, ok := superchain.OPChains[config.ChainID.Uint64()]; ok {
 					conf, err := params.LoadOPStackChainConfig(config.ChainID.Uint64())
 					if err != nil {
```
