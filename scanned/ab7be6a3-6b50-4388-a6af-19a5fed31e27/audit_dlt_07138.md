# [?] core: fix import errors on clique crashes + empty blocks (#19544)

## Summary
Severity: Unknown
Chain: Celo
Component: celo-org/celo-blockchain
Published: 2019-05-10
Source: https://github.com/celo-org/celo-blockchain/commit/6ec6b290511a7433a36a40d1e8c2cca3d9613d6f
Type: security-commit

## Details
core: fix import errors on clique crashes + empty blocks (#19544)

* core: fix import errors on clique crashes + empty blocks

* cosensus/clique, core: add test for the mirrored state issue

* core: address todo question wrt log count

* core: raise a louder warning for non-clique known blocks

## Patch
### consensus/clique/clique_test.go
```diff
@@ -0,0 +1,113 @@
+// Copyright 2019 The go-ethereum Authors
+// This file is part of the go-ethereum library.
+//
+// The go-ethereum library is free software: you can redistribute it and/or modify
+// it under the terms of the GNU Lesser General Public License as published by
+// the Free Software Foundation, either version 3 of the License, or
+// (at your option) any later version.
+//
+// The go-ethereum library is distributed in the hope that it will be useful,
+// but WITHOUT ANY WARRANTY; without even the implied warranty of
+// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
+// GNU Lesser General Public License for more details.
+//
+// You should have received a copy of the GNU Lesser General Public License
+// along with the go-ethereum library. If not, see <http://www.gnu.org/licenses/>.
+
+package clique
+
+import (
+	"math/big"
+	"testing"
+
+	"github.com/ethereum/go-ethereum/common"
+	"github.com/ethereum/go-ethereum/core"
+	"github.com/ethereum/go-ethereum/core/rawdb"
+	"github.com/ethereum/go-ethereum/core/types"
+	"github.com/ethereum/go-ethereum/core/vm"
+	"github.com/ethereum/go-ethereum/crypto"
+	"github.com/ethereum/go-ethereum/params"
+)
+
+// This test case is a repro of an annoying bug that took us forever to catch.
+// In Clique PoA networks (Rinkeby, Görli, etc), consecutive blocks might have
+// the same state root (no block subsidy, empty block). If a node crashes, the
+// chain ends up losing the recent state and needs to regenerate it from blocks
+// already in the database. The bug was that processing the block *prior* to an
+// empty one **also completes** the empty one, ending up in a known-block error.
+func TestReimportMirroredState(t *testing.T) {
+	// Initialize a Clique chain with a single signer
+	var (
+		db     = rawdb.NewMemoryDatabase()
+		key, _ = crypto.HexToECDSA("b71c71a67e1177ad4e901695e1b4b9ee17ae16c6668d313eac2f96dbcda3f291")
+		addr   = crypto.PubkeyToAddress(key.PublicKey)
+		engine = New(params.AllCliqueProtocolChanges.Clique, db)
+		signer = new(types.HomesteadSigner)
+	)
+	genspec := &core.Genesis{
+		ExtraData: make([]byte, extraVanity+common.AddressLength+extraSeal),
+		Alloc: map[common.Address]core.GenesisAccount{
+			addr: {Balance: big.NewInt(1)},
+		},
+	}
+	copy(genspec.ExtraData[extraVanity:], addr[:])
+	genesis := genspec.MustCommit(db)
+
+	// Generate a batch of blocks, each properly signed
+	chain, _ := core.NewBlockChain(db, nil, params.AllCliqueProtocolChanges, engine, vm.Config{}, nil)
+	defer chain.Stop()
+
+	blocks, _ := core.GenerateChain(params.AllCliqueProtocolChanges, genesis, engine, db, 3, func(i int, block *core.BlockGen) {
+		// The chain maker doesn't have access to a chain, so the difficulty will be
+		// lets unset (nil). Set it here to the correct value.
+		block.SetDifficulty(diffInTurn)
+
+		// We want to simulate an empty middle block, having the same state as the
+		// first one. The last is needs a state change again to force a reorg.
+		if i != 1 {
+			tx, err := types.SignTx(types.NewTransaction(block.TxNonce(addr), common.Address{0x00}, new(big.Int), params.TxGas, nil, nil), signer, key)
+			if err != nil {
+				panic(err)
+			}
+			block.AddTxWithChain(chain, tx)
+		}
+	})
+	for i, block := range blocks {
+		header := block.Header()
+		if i > 0 {
+			header.ParentHash = blocks[i-1].Hash()
+		}
+		header.Extra = make([]byte, extraVanity+extraSeal)
+		header.Difficulty = diffInTurn
+
+		sig, _ := crypto.Sign(SealHash(header).Bytes(), key)
+		copy(header.Extra[len(header.Extra)-extraSeal:], sig)
+		blocks[i] = block.WithSeal(header)
+	}
+	// Insert the first two blocks and make sure the chain is valid
+	db = rawdb.NewMemoryDatabase()
+	genspec.MustCommit(db)
+
+	chain, _ = core.NewBlockChain(db, nil, params.AllCliqueProtocolChanges, engine, vm.Config{}, nil)
+	defer chain.Stop()
+
+	if _, err := chain.InsertChain(blocks[:2]); err != nil {
+		t.Fatalf("failed to insert initial blocks: %v", err)
+	}
+	if head := chain.CurrentBlock().NumberU64(); head != 2 {
+		t.Fatalf("chain head mismatch: have %d, want %d", head, 2)
+	}
+
+	// Simulate a crash by creating a new chain on top of the database, without
+	// flushing the dirty states out. Insert the last block, trigerring a sidechain
+	// reimport.
+	chain, _ = core.NewBlockChain(db, nil, params.AllCliqueProtocolChanges, engine, vm.Config{}, nil)
+	defer chain.Stop()
+
+	if _, err := chain.InsertChain(blocks[2:]); err != nil {
+		t.Fatalf("failed to insert final block: %v", err)
+	}
+	if head := chain.CurrentBlock().NumberU64(); head != 3 {
+		t.Fatalf("chain head mismatch: have %d, want %d", head, 3)
+	}
+}
```

### core/blockchain.go
```diff
@@ -1169,7 +1169,9 @@ func (bc *BlockChain) insertChain(chain types.Blocks, verifySeals bool) (int, []
 			if localTd.Cmp(externTd) < 0 {
 				break
 			}
+			log.Debug("Ignoring already known block", "number", block.Number(), "hash", block.Hash())
 			stats.ignored++
+
 			block, err = it.next()
 		}
 		// The remaining blocks are still known blocks, the only scenario here is:
@@ -1181,6 +1183,7 @@ func (bc *BlockChain) insertChain(chain types.Blocks, verifySeals bool) (int, []
 		// `insertChain` while a part of them have higher total difficulty than current
 		// head full block(new pivot point).
 		for block != nil && err == ErrKnownBlock {
+			log.Debug("Writing previously known block", "number", block.Number(), "hash", block.Hash())
 			if err := bc.writeKnownBlock(block); err != nil {
 				return it.index, nil, nil, err
 			}
@@ -1190,15 +1193,16 @@ func (bc *BlockChain) insertChain(chain types.Blocks, verifySeals bool) (int, []
 		}
 		// Falls through to the block import
 	}
-
 	switch {
 	// First block is pruned, insert as sidechain and reorg only if TD grows enough
 	case err == consensus.ErrPrunedAncestor:
+		log.Debug("Pruned ancestor, inserting as sidechain", "number", block.Number(), "hash", block.Hash())
 		return bc.insertSideChain(block, it)
 
 	// First block is future, shove it (and all children) to the future queue (unknown ancestor)
 	case err == consensus.ErrFutureBlock || (err == consensus.ErrUnknownAncestor && bc.futureBlocks.Contains(it.first().ParentHash())):
 		for block != nil && (it.index == 0 || err == consensus.ErrUnknownAncestor) {
+			log.Debug("Future block, postponing import", "number", block.Number(), "hash", block.Hash())
 			if err := bc.addFutureBlock(block); err != nil {
 				return it.index, events, coalescedLogs, err
 			}
@@ -1217,7 +1221,7 @@ func (bc *BlockChain) insertChain(chain types.Blocks, verifySeals bool) (int, []
 		return it.index, events, coalescedLogs, err
 	}
 	// No validation errors for the first block (or chain prefix skipped)
-	for ; block != nil && err == nil; block, err = it.next() {
+	for ; block != nil && err == nil || err == ErrKnownBlock; block, err = it.next() {
 		// If the chain is terminating, stop processing blocks
 		if atomic.LoadInt32(&bc.procInterrupt) == 1 {
 			log.Debug("Premature abort during blocks processing")
@@ -1228,6 +1232,32 @@ func (bc *BlockChain) insertChain(chain types.Blocks, verifySeals bool) (int, []
 			bc.reportBlock(block, nil, ErrBlacklistedHash)
 			return it.index, events, coalescedLogs, ErrBlacklistedHash
 		}
+		// If the block is known (in the middle of the chain), it's a special case for
+		// Clique blocks where they can share state among each other, so importing an
+		// older block might complete the state of the subsequent one. In this case,
+		// just skip the block (we already validated it once fully (and crashed), since
+		// its header and body was already in the database).
+		if err == ErrKnownBlock {
+			logger := log.Debug
+			if bc.chainConfig.Clique == nil {
+				logger = log.Warn
+			}
+			logger("Inserted known block", "number", block.Number(), "hash", block.Hash(),
+				"uncles", len(block.Uncles()), "txs", len(block.Transactions()), "gas", block.GasUsed(),
+				"root", block.Root())
+
+			if err := bc.writeKnownBlock(block); err != nil {
+				return it.index, nil, nil, err
+			}
+			stats.processed++
+
+			// We can assume that logs are empty here, since the only way for consecutive
+			// Clique blocks to have the same state is if there are no transactions.
+			events = append(events, ChainEvent{block, block.Hash(), nil})
+			lastCanon = block
+
+			continue
+		}
 		// Retrieve the parent block and it's state to execute on top
 		start := time.Now()
 
@@ -1327,6 +1357,14 @@ func (bc *BlockChain) insertChain(chain types.Blocks, verifySeals bool) (int, []
 				"txs", len(block.Transactions()), "gas", block.GasUsed(), "uncles", len(block.Uncles()),
 				"root", block.Root())
 			events = append(events, ChainSideEvent{block})
+
+		default:
+			// This in theory is impossible, but lets be nice to our future selves and leave
+			// a log, instead of trying to track down blocks imports that don't emit logs.
+			log.Warn("Inserted block with unknown status", "number", block.Number(), "hash", block.Hash(),
+				"diff", block.Difficulty(), "elapsed", common.PrettyDuration(time.Since(start)),
+				"txs", len(block.Transactions()), "gas", block.GasUsed(), "uncles", len(block.Uncles()),
+				"root", block.Root())
 		}
 		stats.processed++
 		stats.usedGas += usedGas
```

### core/chain_makers.go
```diff
@@ -71,6 +71,13 @@ func (b *BlockGen) SetNonce(nonce types.BlockNonce) {
 	b.header.Nonce = nonce
 }
 
+// SetDifficulty sets the difficulty field of the generated block. This method is
+// useful for Clique tests where the difficulty does not depend on time. For the
+// ethash tests, please use OffsetTime, which implicitly recalculates the diff.
+func (b *BlockGen) SetDifficulty(diff *big.Int) {
+	b.header.Difficulty = diff
+}
+
 // AddTx adds a transaction to the generated block. If no coinbase has
 // been set, the block's coinbase is set to the zero address.
 //
```
