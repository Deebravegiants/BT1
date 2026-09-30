# [?] Patch crashes on mobile from rounded state db (#700)

## Summary
Severity: Unknown
Chain: Celo
Component: celo-org/celo-blockchain
Published: 2019-12-10
Source: https://github.com/celo-org/celo-blockchain/commit/30a841d9f8a3db44c2b07e7c8b47ea3255cdce39
Type: security-commit

## Details
Patch crashes on mobile from rounded state db (#700)

## Patch
### mobile/geth.go
```diff
@@ -193,6 +193,8 @@ func NewNode(datadir string, config *NodeConfig) (stack *Node, _ error) {
 		ethConf.DatabaseCache = config.EthereumDatabaseCache
 		// Use an in memory DB for validatorEnode table
 		ethConf.Istanbul.ValidatorEnodeDBPath = ""
+		// Use an in memory DB for roundState table
+		ethConf.Istanbul.RoundStateDBPath = ""
 		if err := rawStack.Register(func(ctx *node.ServiceContext) (node.Service, error) {
 			return les.New(ctx, &ethConf)
 		}); err != nil {
```
