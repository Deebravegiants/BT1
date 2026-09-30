# [?] Node crash issue fix

## Summary
Severity: Unknown
Chain: Quorum
Component: Consensys-inc-archive/quorum
Published: 2018-10-05
Source: https://github.com/Consensys-inc-archive/quorum/commit/9ab2f224d91ff558aca24e92d76e421856ff990b
Type: security-commit

## Details
Node crash issue fix

## Patch
### core/blockchain.go
```diff
@@ -936,16 +936,16 @@ func (bc *BlockChain) WriteBlockWithState(block *types.Block, receipts []*types.
 	triedb := bc.stateCache.TrieDB()
 
 	// Explicit commit for privateStateTriedb to handle Raft
-	if privateState != nil {
-		privateRoot, err := privateState.Commit(bc.chainConfig.IsEIP158(block.Number()))
-		if err != nil {
-			return NonStatTy, err
-		}
-		privateTriedb := bc.privateStateCache.TrieDB()
-		if err := privateTriedb.Commit(privateRoot, false); err != nil {
-			return NonStatTy, err
-		}
-	}
+	// if privateState != nil {
+	// 	privateRoot, err := privateState.Commit(bc.chainConfig.IsEIP158(block.Number()))
+	// 	if err != nil {
+	// 		return NonStatTy, err
+	// 	}
+	// 	privateTriedb := bc.privateStateCache.TrieDB()
+	// 	if err := privateTriedb.Commit(privateRoot, false); err != nil {
+	// 		return NonStatTy, err
+	// 	}
+	// }
 
 	// If we're running an archive node, always flush
 	if bc.cacheConfig.Disabled {
@@ -1213,7 +1213,7 @@ func (bc *BlockChain) insertChain(chain types.Blocks) (int, []interface{}, []*ty
 		}
 
 		// Quorum
-		privateStateRoot := GetPrivateStateRoot(bc.db, parent.Root())
+		privateStateRoot := rawdb.GetPrivateStateRoot(bc.db, parent.Root())
 		privateState, err := stateNew(privateStateRoot, bc.privateStateCache)
 		if err != nil {
 			return i, events, coalescedLogs, err
@@ -1252,7 +1252,7 @@ func (bc *BlockChain) insertChain(chain types.Blocks) (int, []interface{}, []*ty
 		if err != nil {
 			return i, events, coalescedLogs, err
 		}
-		if err := WritePrivateBlockBloom(bc.db, block.NumberU64(), privateReceipts); err != nil {
+		if err := rawdb.WritePrivateBlockBloom(bc.db, block.NumberU64(), privateReceipts); err != nil {
 			return i, events, coalescedLogs, err
 		}
 		switch status {
```

### core/rawdb/accessors_private.go
```diff
@@ -0,0 +1,57 @@
+// Copyright 2018 The go-ethereum Authors
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
+package rawdb
+
+import (
+	"github.com/ethereum/go-ethereum/common"
+	"github.com/ethereum/go-ethereum/core/types"
+)
+
+// The fields below define the low level database schema prefixing.
+var (
+	privateRootPrefix          = []byte("P")
+	privateblockReceiptsPrefix = []byte("Pr") // blockReceiptsPrefix + num (uint64 big endian) + hash -> block receipts
+	privateReceiptPrefix       = []byte("Prs")
+	privateBloomPrefix         = []byte("Pb")
+)
+
+//GetPrivateStateRoot utility to get private hate root hash
+func GetPrivateStateRoot(db DatabaseReader, blockRoot common.Hash) common.Hash {
+	root, _ := db.Get(append(privateRootPrefix, blockRoot[:]...))
+	return common.BytesToHash(root)
+}
+
+//WritePrivateStateRoot utility to write private root hash
+func WritePrivateStateRoot(db DatabaseWriter, blockRoot, root common.Hash) error {
+	return db.Put(append(privateRootPrefix, blockRoot[:]...), root[:])
+}
+
+// WritePrivateBlockBloom creates a bloom filter for the given receipts and saves it to the database
+// with the number given as identifier (i.e. block number).
+func WritePrivateBlockBloom(db DatabaseWriter, number uint64, receipts types.Receipts) error {
+	rbloom := types.CreateBloom(receipts)
+	return db.Put(append(privateBloomPrefix, encodeBlockNumber(number)...), rbloom[:])
+}
+
+// GetPrivateBlockBloom retrieves the private bloom associated with the given number.
+func GetPrivateBlockBloom(db DatabaseReader, number uint64) (bloom types.Bloom) {
+	data, _ := db.Get(append(privateBloomPrefix, encodeBlockNumber(number)...))
+	if len(data) > 0 {
+		bloom = types.BytesToBloom(data)
+	}
+	return bloom
+}
```

### miner/worker.go
```diff
@@ -28,6 +28,7 @@ import (
 	"github.com/ethereum/go-ethereum/consensus"
 	"github.com/ethereum/go-ethereum/consensus/misc"
 	"github.com/ethereum/go-ethereum/core"
+	"github.com/ethereum/go-ethereum/core/rawdb"
 	"github.com/ethereum/go-ethereum/core/state"
 	"github.com/ethereum/go-ethereum/core/types"
 	"github.com/ethereum/go-ethereum/core/vm"
@@ -336,7 +337,7 @@ func (self *worker) wait() {
 
 			// write private transacions
 			privateStateRoot, _ := work.privateState.Commit(self.config.IsEIP158(block.Number()))
-			core.WritePrivateStateRoot(self.chainDb, block.Root(), privateStateRoot)
+			rawdb.WritePrivateStateRoot(self.chainDb, block.Root(), privateStateRoot)
 			allReceipts := mergeReceipts(work.receipts, work.privateReceipts)
 
 			stat, err := self.chain.WriteBlockWithState(block, allReceipts, work.state, nil)
```
