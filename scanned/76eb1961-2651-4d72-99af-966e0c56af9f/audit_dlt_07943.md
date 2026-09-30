# [?] fix(core): Potential crash loop at SAE upgrade (#5755)

## Summary
Severity: Unknown
Chain: Avalanche
Component: ava-labs/avalanchego
Published: 2026-07-29
Source: https://github.com/ava-labs/avalanchego/commit/23bb20e720e0a2245ac23db4069f2a921ae6f7bc
Type: security-commit

## Details
fix(core): Potential crash loop at SAE upgrade (#5755)

## Patch
### graft/coreth/core/blockchain.go
```diff
@@ -761,6 +761,21 @@ func (bc *BlockChain) loadLastState(lastAcceptedHash common.Hash) error {
 		return fmt.Errorf("could not load last accepted block")
 	}
 
+	// SAE requires these values to be set to the last accepted hash on
+	// transition. Nodes that do not accept any blocks after upgrading before
+	// transition wouldn't otherwise correctly set these values.
+	{
+		lastAcceptedHash := bc.lastAccepted.Hash()
+		if finalized := rawdb.ReadFinalizedBlockHash(bc.db); finalized != lastAcceptedHash {
+			log.Info("Repairing finalized block hash", "from", finalized, "to", lastAcceptedHash)
+			rawdb.WriteFinalizedBlockHash(bc.db, lastAcceptedHash)
+		}
+		if headFast := rawdb.ReadHeadFastBlockHash(bc.db); headFast != lastAcceptedHash {
+			log.Info("Repairing head fast block hash", "from", headFast, "to", lastAcceptedHash)
+			rawdb.WriteHeadFastBlockHash(bc.db, lastAcceptedHash)
+		}
+	}
+
 	// This ensures that the head block is updated to the last accepted block on startup
 	if err := bc.setPreference(bc.lastAccepted); err != nil {
 		return fmt.Errorf("failed to set preference to last accepted block while loading last state: %w", err)
```

### graft/coreth/core/blockchain_test.go
```diff
@@ -46,6 +46,8 @@ import (
 	"github.com/ava-labs/libevm/crypto"
 	"github.com/ava-labs/libevm/eth/tracers/logger"
 	"github.com/ava-labs/libevm/ethdb"
+	"github.com/stretchr/testify/require"
+
 	ethparams "github.com/ava-labs/libevm/params"
 )
 
@@ -1389,3 +1391,51 @@ func TestEIP3651(t *testing.T) {
 		t.Fatalf("sender balance incorrect: expected %d, got %d", expected, actual)
 	}
 }
+
+func TestLegacyMarkersRepairedOnStartup(t *testing.T) {
+	key, _ := crypto.HexToECDSA("b71c71a67e1177ad4e901695e1b4b9ee17ae16c6668d313eac2f96dbcda3f291")
+	addr := crypto.PubkeyToAddress(key.PublicKey)
+	db := rawdb.NewMemoryDatabase()
+	gspec := &Genesis{
+		Config: &params.ChainConfig{HomesteadBlock: new(big.Int)},
+		Alloc:  types.GenesisAlloc{addr: {Balance: big.NewInt(1000000)}},
+	}
+
+	blockchain, err := createBlockChain(db, pruningConfig, gspec, common.Hash{})
+	require.NoError(t, err, "createBlockChain()")
+
+	_, chain, _, err := GenerateChainWithGenesis(gspec, blockchain.engine, 3, 10, func(int, *BlockGen) {})
+	require.NoError(t, err, "GenerateChainWithGenesis()")
+
+	_, err = blockchain.InsertChain(chain)
+	require.NoErrorf(t, err, "%T.InsertChain()", blockchain)
+	lastAccepted := chain[1]
+	for _, b := range chain[:2] {
+		require.NoErrorf(t, blockchain.Accept(b), "%T.Accept()", blockchain)
+	}
+	blockchain.DrainAcceptorQueue()
+	genesisHash := blockchain.genesisBlock.Hash()
+	lastAcceptedHash := lastAccepted.Hash()
+	lastVerifiedHash := chain[len(chain)-1].Hash()
+	blockchain.Stop()
+
+	require.Equal(t, lastAcceptedHash, rawdb.ReadFinalizedBlockHash(db), "finalized block hash after normal shutdown")
+	require.Equal(t, lastVerifiedHash, rawdb.ReadHeadFastBlockHash(db), "head fast block hash after normal shutdown")
+
+	// Emulate legacy markers
+	legacyFinalizedBlockKey := []byte("LastFinalized") // mirrors the unexported [rawdb] schema key
+	require.NoErrorf(t, db.Delete(legacyFinalizedBlockKey), "%T.Delete(%q)", db, legacyFinalizedBlockKey)
+	require.Equal(t, common.Hash{}, rawdb.ReadFinalizedBlockHash(db), "finalized block hash after simulating a legacy database")
+	rawdb.WriteHeadFastBlockHash(db, genesisHash)
+
+	restarted, err := createBlockChain(db, pruningConfig, gspec, lastAcceptedHash)
+	require.NoError(t, err, "createBlockChain() on restart")
+	defer restarted.Stop()
+
+	require.Equal(t, lastAcceptedHash, rawdb.ReadFinalizedBlockHash(db), "repaired finalized block hash")
+	require.Equal(t, lastAcceptedHash, rawdb.ReadHeadFastBlockHash(db), "repaired head fast block hash")
+
+	// The repair must use the last accepted block, whose state [BlockChain.Stop]
+	// commits, because the block settled from must have its state on disk.
+	require.True(t, restarted.HasState(lastAccepted.Root()), "state of repaired marker block is on disk")
+}
```

### graft/subnet-evm/core/blockchain.go
```diff
@@ -778,6 +778,21 @@ func (bc *BlockChain) loadLastState(lastAcceptedHash common.Hash) error {
 		return fmt.Errorf("could not load last accepted block")
 	}
 
+	// SAE requires these values to be set to the last accepted hash on
+	// transition. Nodes that do not accept any blocks after upgrading before
+	// transition wouldn't otherwise correctly set these values.
+	{
+		lastAcceptedHash := bc.lastAccepted.Hash()
+		if finalized := rawdb.ReadFinalizedBlockHash(bc.db); finalized != lastAcceptedHash {
+			log.Info("Repairing finalized block hash", "from", finalized, "to", lastAcceptedHash)
+			rawdb.WriteFinalizedBlockHash(bc.db, lastAcceptedHash)
+		}
+		if headFast := rawdb.ReadHeadFastBlockHash(bc.db); headFast != lastAcceptedHash {
+			log.Info("Repairing head fast block hash", "from", headFast, "to", lastAcceptedHash)
+			rawdb.WriteHeadFastBlockHash(bc.db, lastAcceptedHash)
+		}
+	}
+
 	// This ensures that the head block is updated to the last accepted block on startup
 	if err := bc.setPreference(bc.lastAccepted); err != nil {
 		return fmt.Errorf("failed to set preference to last accepted block while loading last state: %w", err)
@@ -860,7 +875,7 @@ func (bc *BlockChain) writeHeadBlock(block *types.Block) {
 	// Add the block to the canonical chain number scheme and mark as the head
 	batch := bc.db.NewBatch()
 	rawdb.WriteCanonicalHash(batch, block.Hash(), block.NumberU64())
-	rawdb.WriteHeadBlockHash(batch, block.Hash())
+	rawdb.WriteHeadFastBlockHash(batch, block.Hash())
 	rawdb.WriteHeadBlockHash(batch, block.Hash())
 	rawdb.WriteHeadHeaderHash(batch, block.Hash())
 
```

### graft/subnet-evm/core/blockchain_test.go
```diff
@@ -41,6 +41,7 @@ import (
 	"github.com/ava-labs/libevm/crypto"
 	"github.com/ava-labs/libevm/eth/tracers/logger"
 	"github.com/ava-labs/libevm/ethdb"
+	"github.com/stretchr/testify/require"
 
 	"github.com/ava-labs/avalanchego/graft/evm/core/state/pruner"
 	"github.com/ava-labs/avalanchego/graft/subnet-evm/consensus/dummy"
@@ -1343,3 +1344,51 @@ func TestEIP3651(t *testing.T) {
 		t.Fatalf("sender balance incorrect: expected %d, got %d", expected, actual)
 	}
 }
+
+func TestLegacyMarkersRepairedOnStartup(t *testing.T) {
+	key, _ := crypto.HexToECDSA("b71c71a67e1177ad4e901695e1b4b9ee17ae16c6668d313eac2f96dbcda3f291")
+	addr := crypto.PubkeyToAddress(key.PublicKey)
+	db := rawdb.NewMemoryDatabase()
+	gspec := &Genesis{
+		Config: &params.ChainConfig{HomesteadBlock: new(big.Int)},
+		Alloc:  types.GenesisAlloc{addr: {Balance: big.NewInt(1000000)}},
+	}
+
+	blockchain, err := createBlockChain(db, pruningConfig, gspec, common.Hash{})
+	require.NoError(t, err, "createBlockChain()")
+
+	_, chain, _, err := GenerateChainWithGenesis(gspec, blockchain.engine, 3, 10, func(int, *BlockGen) {})
+	require.NoError(t, err, "GenerateChainWithGenesis()")
+
+	_, err = blockchain.InsertChain(chain)
+	require.NoErrorf(t, err, "%T.InsertChain()", blockchain)
+	lastAccepted := chain[1]
+	for _, b := range chain[:2] {
+		require.NoErrorf(t, blockchain.Accept(b), "%T.Accept()", blockchain)
+	}
+	blockchain.DrainAcceptorQueue()
+	genesisHash := blockchain.genesisBlock.Hash()
+	lastAcceptedHash := lastAccepted.Hash()
+	lastVerifiedHash := chain[len(chain)-1].Hash()
+	blockchain.Stop()
+
+	require.Equal(t, lastAcceptedHash, rawdb.ReadFinalizedBlockHash(db), "finalized block hash after normal shutdown")
+	require.Equal(t, lastVerifiedHash, rawdb.ReadHeadFastBlockHash(db), "head fast block hash after normal shutdown")
+
+	// Emulate legacy markers
+	legacyFinalizedBlockKey := []byte("LastFinalized") // mirrors the unexported [rawdb] schema key
+	require.NoErrorf(t, db.Delete(legacyFinalizedBlockKey), "%T.Delete(%q)", db, legacyFinalizedBlockKey)
+	require.Equal(t, common.Hash{}, rawdb.ReadFinalizedBlockHash(db), "finalized block hash after simulating a legacy database")
+	rawdb.WriteHeadFastBlockHash(db, genesisHash)
+
+	restarted, err := createBlockChain(db, pruningConfig, gspec, lastAcceptedHash)
+	require.NoError(t, err, "createBlockChain() on restart")
+	defer restarted.Stop()
+
+	require.Equal(t, lastAcceptedHash, rawdb.ReadFinalizedBlockHash(db), "repaired finalized block hash")
+	require.Equal(t, lastAcceptedHash, rawdb.ReadHeadFastBlockHash(db), "repaired head fast block hash")
+
+	// The repair must use the last accepted block, whose state [BlockChain.Stop]
+	// commits, because the block settled from must have its state on disk.
+	require.True(t, restarted.HasState(lastAccepted.Root()), "state of repaired marker block is on disk")
+}
```
