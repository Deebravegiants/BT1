# [?] Fix potential nil pointer dereference panic in superchain overrides

## Summary
Severity: Unknown
Chain: Optimism
Component: ethereum-optimism/op-geth
Published: 2023-10-27
Source: https://github.com/ethereum-optimism/op-geth/commit/ac6f77be565d270d6a3ca66359a409d9a463e914
Type: security-commit

## Details
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
