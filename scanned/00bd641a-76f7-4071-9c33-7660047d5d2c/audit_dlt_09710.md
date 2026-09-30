# [?] eth/filters: fix test panic for london block without basefee configured

## Summary
Severity: Unknown
Chain: Ethereum Classic
Component: etclabscore/core-geth
Published: 2021-08-25
Source: https://github.com/etclabscore/core-geth/commit/ecc82bb6e2efdaa503b1e21ef9ab3ecadc4c4c6e
Type: security-commit

## Details
eth/filters: fix test panic for london block without basefee configured

Date: 2021-08-25 06:20:37-05:00
Signed-off-by: meows <b5c6@protonmail.com>

## Patch
### eth/filters/filter_system_test.go
```diff
@@ -233,7 +233,8 @@ func TestSideBlockSubscription(t *testing.T) {
 		db              = rawdb.NewMemoryDatabase()
 		backend         = &testBackend{db: db}
 		api             = NewPublicFilterAPI(backend, false, deadline)
-		genesis         = core.MustCommitGenesis(db, new(genesisT.Genesis))
+		gspec           = &genesisT.Genesis{BaseFee: big.NewInt(vars.InitialBaseFee)}
+		genesis         = core.MustCommitGenesis(db, gspec)
 		chain, _        = core.GenerateChain(params.TestChainConfig, genesis, ethash.NewFaker(), db, 10, func(i int, gen *core.BlockGen) {})
 		chainSideEvents = []core.ChainSideEvent{}
 	)
```
