# [?] miner: fixed race condition in tests (#21664)

## Summary
Severity: Unknown
Chain: Ethereum
Component: ethereum/go-ethereum
Published: 2020-10-20
Source: https://github.com/ethereum/go-ethereum/commit/6e7137103c63f471bf577d857f179110622d8804
Type: security-commit

## Details
miner: fixed race condition in tests (#21664)

## Patch
### miner/miner_test.go
```diff
@@ -22,7 +22,7 @@ import (
 	"time"
 
 	"github.com/ethereum/go-ethereum/common"
-	"github.com/ethereum/go-ethereum/consensus/ethash"
+	"github.com/ethereum/go-ethereum/consensus/clique"
 	"github.com/ethereum/go-ethereum/core"
 	"github.com/ethereum/go-ethereum/core/rawdb"
 	"github.com/ethereum/go-ethereum/core/state"
@@ -31,7 +31,6 @@ import (
 	"github.com/ethereum/go-ethereum/eth/downloader"
 	"github.com/ethereum/go-ethereum/ethdb/memorydb"
 	"github.com/ethereum/go-ethereum/event"
-	"github.com/ethereum/go-ethereum/params"
 	"github.com/ethereum/go-ethereum/trie"
 )
 
@@ -243,26 +242,20 @@ func createMiner(t *testing.T) (*Miner, *event.TypeMux) {
 	if err != nil {
 		t.Fatalf("can't create new chain config: %v", err)
 	}
-	// Create event Mux
-	mux := new(event.TypeMux)
 	// Create consensus engine
-	engine := ethash.New(ethash.Config{}, []string{}, false)
-	engine.SetThreads(-1)
-	// Create isLocalBlock
-	isLocalBlock := func(block *types.Block) bool {
-		return true
-	}
+	engine := clique.New(chainConfig.Clique, chainDB)
 	// Create Ethereum backend
-	limit := uint64(1000)
-	bc, err := core.NewBlockChain(chainDB, new(core.CacheConfig), chainConfig, engine, vm.Config{}, isLocalBlock, &limit)
+	bc, err := core.NewBlockChain(chainDB, nil, chainConfig, engine, vm.Config{}, nil, nil)
 	if err != nil {
 		t.Fatalf("can't create new chain %v", err)
 	}
-	statedb, _ := state.New(common.Hash{}, state.NewDatabase(rawdb.NewMemoryDatabase()), nil)
+	statedb, _ := state.New(common.Hash{}, state.NewDatabase(chainDB), nil)
 	blockchain := &testBlockChain{statedb, 10000000, new(event.Feed)}
 
-	pool := core.NewTxPool(testTxPoolConfig, params.TestChainConfig, blockchain)
+	pool := core.NewTxPool(testTxPoolConfig, chainConfig, blockchain)
 	backend := NewMockBackend(bc, pool)
+	// Create event Mux
+	mux := new(event.TypeMux)
 	// Create Miner
-	return New(backend, &config, chainConfig, mux, engine, isLocalBlock), mux
+	return New(backend, &config, chainConfig, mux, engine, nil), mux
 }
```
