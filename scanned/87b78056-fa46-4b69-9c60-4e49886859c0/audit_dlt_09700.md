# [?] eth/filters: TestSideBlockSubscription: fix panic b/c nil config on genesis

## Summary
Severity: Unknown
Chain: Ethereum Classic
Component: etclabscore/core-geth
Published: 2024-02-29
Source: https://github.com/etclabscore/core-geth/commit/1c26717c3b55f596241d9d87d0bb6eabf3f04a4e
Type: security-commit

## Details
eth/filters: TestSideBlockSubscription: fix panic b/c nil config on genesis

Date: 2024-02-29 07:30:31-07:00
Signed-off-by: meows <b5c6@protonmail.com>

## Patch
### eth/filters/filter_system_test.go
```diff
@@ -263,10 +263,13 @@ func TestSideBlockSubscription(t *testing.T) {
 	t.Parallel()
 
 	var (
-		db              = rawdb.NewMemoryDatabase()
-		backend, sys    = newTestFilterSystem(t, db, Config{})
-		api             = NewFilterAPI(sys, false)
-		gspec           = &genesisT.Genesis{BaseFee: big.NewInt(vars.InitialBaseFee)}
+		db           = rawdb.NewMemoryDatabase()
+		backend, sys = newTestFilterSystem(t, db, Config{})
+		api          = NewFilterAPI(sys, false)
+		gspec        = &genesisT.Genesis{
+			Config:  params.TestChainConfig,
+			BaseFee: big.NewInt(vars.InitialBaseFee),
+		}
 		genesis         = core.MustCommitGenesis(db, triedb.NewDatabase(db, nil), gspec)
 		chain, _        = core.GenerateChain(params.TestChainConfig, genesis, ethash.NewFaker(), db, 10, func(i int, gen *core.BlockGen) {})
 		chainSideEvents = []core.ChainSideEvent{}
```
