# [?] Merge branch 'dev' of github.com:klaytn/klaytn into sc-concurrency-crash-fix

## Summary
Severity: Unknown
Chain: Kaia
Component: kaiachain/kaia
Published: 2022-06-29
Source: https://github.com/kaiachain/kaia/commit/ba5c17379612b621952747079474b4c9ad204803
Type: security-commit

## Details
Merge branch 'dev' of github.com:klaytn/klaytn into sc-concurrency-crash-fix

## Patch
### accounts/abi/bind/backends/simulated.go
```diff
@@ -93,11 +93,9 @@ func NewSimulatedBackendWithDatabase(database database.DBManager, alloc blockcha
 // NewSimulatedBackendWithGasPrice creates a new binding backend using a simulated blockchain with a given unitPrice.
 // for testing purposes.
 func NewSimulatedBackendWithGasPrice(alloc blockchain.GenesisAlloc, unitPrice uint64) *SimulatedBackend {
-	// Without changing `params.AllGxhashProtocolChanges`,
-	// the copied config is used for no side effect of other tests
-	cfg := *params.AllGxhashProtocolChanges
+	cfg := params.AllGxhashProtocolChanges.Copy()
 	cfg.UnitPrice = unitPrice
-	return NewSimulatedBackendWithDatabase(database.NewMemoryDBManager(), alloc, &cfg)
+	return NewSimulatedBackendWithDatabase(database.NewMemoryDBManager(), alloc, cfg)
 }
 
 // NewSimulatedBackend creates a new binding backend using a simulated blockchain
```

### blockchain/blockchain.go
```diff
@@ -108,10 +108,15 @@ const (
 
 const (
 	DefaultTriesInMemory = 128
-	// BlockChainVersion ensures that an incompatible database forces a resync from scratch.
-	BlockChainVersion    = 3
 	DefaultBlockInterval = 128
 	MaxPrefetchTxs       = 20000
+
+	// BlockChainVersion ensures that an incompatible database forces a resync from scratch.
+	// Changelog:
+	// - Version 4
+	// The following incompatible database changes were added:
+	//   * New scheme for contract code in order to separate the codes and trie nodes
+	BlockChainVersion = 4
 )
 
 // CacheConfig contains the configuration values for the 1) stateDB caching and
@@ -976,12 +981,30 @@ func (bc *BlockChain) GetLogsByHash(hash common.Hash) [][]*types.Log {
 	return logs
 }
 
-// TrieNode retrieves a blob of data associated with a trie node (or code hash)
+// TrieNode retrieves a blob of data associated with a trie node
 // either from ephemeral in-memory cache, or from persistent storage.
 func (bc *BlockChain) TrieNode(hash common.Hash) ([]byte, error) {
 	return bc.stateCache.TrieDB().Node(hash)
 }
 
+// ContractCode retrieves a blob of data associated with a contract hash
+// either from ephemeral in-memory cache, or from persistent storage.
+func (bc *BlockChain) ContractCode(hash common.Hash) ([]byte, error) {
+	return bc.stateCache.ContractCode(hash)
+}
+
+// ContractCodeWithPrefix retrieves a blob of data associated with a contract
+// hash either from ephemeral in-memory cache, or from persistent storage.
+//
+// If the code doesn't exist in the in-memory cache, check the storage with
+// new code scheme.
+func (bc *BlockChain) ContractCodeWithPrefix(hash common.Hash) ([]byte, error) {
+	type codeReader interface {
+		ContractCodeWithPrefix(codeHash common.Hash) ([]byte, error)
+	}
+	return bc.stateCache.(codeReader).ContractCodeWithPrefix(hash)
+}
+
 // Stop stops the blockchain service. If any imports are currently in progress
 // it will abort them using the procInterrupt.
 func (bc *BlockChain) Stop() {
```

### blockchain/genesis_test.go
```diff
@@ -348,18 +348,16 @@ func TestSetupGenesis(t *testing.T) {
 }
 
 func genCypressGenesisBlock() *Genesis {
-	copyOfCypressChainConfig := *params.CypressChainConfig
 	genesis := DefaultGenesisBlock()
-	genesis.Config = &copyOfCypressChainConfig
+	genesis.Config = params.CypressChainConfig.Copy()
 	genesis.Governance = SetGenesisGovernance(genesis)
 	InitDeriveSha(genesis.Config.DeriveShaImpl)
 	return genesis
 }
 
 func genBaobabGenesisBlock() *Genesis {
-	copyOfBaobabChainConfig := *params.BaobabChainConfig
 	genesis := DefaultBaobabGenesisBlock()
-	genesis.Config = &copyOfBaobabChainConfig
+	genesis.Config = params.BaobabChainConfig.Copy()
 	genesis.Governance = SetGenesisGovernance(genesis)
 	InitDeriveSha(genesis.Config.DeriveShaImpl)
 	return genesis
```

### blockchain/headerchain.go
```diff
@@ -201,7 +201,15 @@ func (hc *HeaderChain) ValidateHeaderChain(chain []*types.Header, checkFreq int)
 	}
 	seals[len(seals)-1] = true // Last should always be verified to avoid junk
 
-	abort, results := hc.engine.VerifyHeaders(hc, chain, seals)
+	var (
+		abort   chan<- struct{}
+		results <-chan error
+	)
+	if hc.engine.CanVerifyHeadersConcurrently() {
+		abort, results = hc.engine.VerifyHeaders(hc, chain, seals)
+	} else {
+		abort, results = hc.engine.PreprocessHeaderVerification(chain)
+	}
 	defer close(abort)
 
 	// Iterate over the headers and ensure they all check out
@@ -247,6 +255,11 @@ func (hc *HeaderChain) InsertHeaderChain(chain []*types.Header, writeHeader WhCa
 			stats.ignored++
 			continue
 		}
+		if !hc.engine.CanVerifyHeadersConcurrently() {
+			if err := hc.engine.VerifyHeader(hc, header, true); err != nil {
+				return i, err
+			}
+		}
 		if err := writeHeader(header); err != nil {
 			return i, err
 		}
```

### blockchain/state/database.go
```diff
@@ -21,8 +21,10 @@
 package state
 
 import (
+	"errors"
 	"fmt"
 
+	"github.com/VictoriaMetrics/fastcache"
 	"github.com/klaytn/klaytn/common"
 	"github.com/klaytn/klaytn/storage/database"
 	"github.com/klaytn/klaytn/storage/statedb"
@@ -32,6 +34,9 @@ const (
 	// Number of codehash->size associations to keep
 	codeSizeCacheSize = 100000
 
+	// Cache size granted for caching clean code.
+	codeCacheSize = 64 * 1024 * 1024
+
 	// Number of shards in cache
 	shardsCodeSizeCache = 4096
 )
@@ -52,6 +57,9 @@ type Database interface {
 	// ContractCode retrieves a particular contract's code.
 	ContractCode(codeHash common.Hash) ([]byte, error)
 
+	// DeleteCode deletes a particular contract's code.
+	DeleteCode(codeHash common.Hash)
+
 	// ContractCodeSize retrieves a particular contracts code's size.
 	ContractCodeSize(codeHash common.Hash) (int, error)
 
@@ -134,6 +142,7 @@ func NewDatabaseWithNewCache(db database.DBManager, cacheConfig *statedb.TrieNod
 	return &cachingDB{
 		db:            statedb.NewDatabaseWithNewCache(db, cacheConfig),
 		codeSizeCache: getCodeSizeCache(),
+		codeCache:     fastcache.New(codeCacheSize),
 	}
 }
 
@@ -144,12 +153,14 @@ func NewDatabaseWithExistingCache(db database.DBManager, cache statedb.TrieNodeC
 	return &cachingDB{
 		db:            statedb.NewDatabaseWithExistingCache(db, cache),
 		codeSizeCache: getCodeSizeCache(),
+		codeCache:     fastcache.New(codeCacheSize),
 	}
 }
 
 type cachingDB struct {
 	db            *statedb.Database
 	codeSizeCache common.Cache
+	codeCache     *fastcache.Cache
 }
 
 // OpenTrie opens the main account trie at a specific root hash.
@@ -184,11 +195,38 @@ func (db *cachingDB) CopyTrie(t Trie) Trie {
 
 // ContractCode retrieves a particular contract's code.
 func (db *cachingDB) ContractCode(codeHash common.Hash) ([]byte, error) {
-	code, err := db.db.Node(codeHash)
-	if err == nil {
+	if code := db.codeCache.Get(nil, codeHash.Bytes()); len(code) > 0 {
+		return code, nil
+	}
+	code := db.db.DiskDB().ReadCode(codeHash)
+	if len(code) > 0 {
+		db.codeCache.Set(codeHash.Bytes(), code)
+		db.codeSizeCache.Add(codeHash, len(code))
+		return code, nil
+	}
+	return nil, errors.New("not found")
+}
+
+// DeleteCode deletes a particular contract's code.
+func (db *cachingDB) DeleteCode(codeHash common.Hash) {
+	db.codeCache.Del(codeHash.Bytes())
+	db.db.DiskDB().DeleteCode(codeHash)
+}
+
+// ContractCodeWithPrefix retrieves a particular contract's code. If the
+// code can't be found in the cache, then check the existence with **new**
+// db scheme.
+func (db *cachingDB) ContractCodeWithPrefix(codeHash common.Hash) ([]byte, error) {
+	if code := db.codeCache.Get(nil, codeHash.Bytes()); len(code) > 0 {
+		return code, nil
+	}
+	code := db.db.DiskDB().ReadCodeWithPrefix(codeHash)
+	if len(code) > 0 {
+		db.codeCache.Set(codeHash.Bytes(), code)
 		db.codeSizeCache.Add(codeHash, len(code))
+		return code, nil
 	}
-	return code, err
+	return nil, errors.New("not found")
 }
 
 // ContractCodeSize retrieves a particular contracts code's size.
```

### blockchain/state/iterator_test.go
```diff
@@ -30,6 +30,7 @@ import (
 func TestNodeIteratorCoverage(t *testing.T) {
 	// Create some arbitrary test state to iterate
 	db, root, _ := makeTestState(t)
+	db.TrieDB().Commit(root, false, 0)
 
 	state, err := New(root, db, nil)
 	if err != nil {
@@ -44,7 +45,10 @@ func TestNodeIteratorCoverage(t *testing.T) {
 	}
 	// Cross check the iterated hashes and the database/nodepool content
 	for hash := range hashes {
-		if _, err := db.TrieDB().Node(hash); err != nil {
+		if _, err = db.TrieDB().Node(hash); err != nil {
+			_, err = db.ContractCode(hash)
+		}
+		if err != nil {
 			t.Errorf("failed to retrieve reported node %x", hash)
 		}
 	}
@@ -59,6 +63,9 @@ func TestNodeIteratorCoverage(t *testing.T) {
 		if bytes.HasPrefix(key, []byte("secure-key-")) {
 			continue
 		}
+		if bytes.Compare(emptyCode[:], common.BytesToHash(key).Bytes()) == 0 {
+			continue
+		}
 		if _, ok := hashes[common.BytesToHash(key)]; !ok {
 			t.Errorf("state entry not reported %x", key)
 		}
```

### blockchain/state/statedb.go
```diff
@@ -1006,7 +1006,7 @@ func (s *StateDB) Commit(deleteEmptyObjects bool) (root common.Hash, err error)
 			if stateObject.IsProgramAccount() {
 				// Write any contract code associated with the state object.
 				if stateObject.code != nil && stateObject.dirtyCode {
-					s.db.TrieDB().InsertBlob(common.BytesToHash(stateObject.CodeHash()), stateObject.code)
+					s.db.TrieDB().DiskDB().WriteCode(common.BytesToHash(stateObject.CodeHash()), stateObject.code)
 					stateObject.dirtyCode = false
 				}
 				// Write any storage changes in the state object to its storage trie.
@@ -1029,7 +1029,7 @@ func (s *StateDB) Commit(deleteEmptyObjects bool) (root common.Hash, err error)
 	if EnabledExpensive {
 		defer func(start time.Time) { s.AccountCommits += time.Since(start) }(time.Now())
 	}
-	root, err = s.trie.Commit(func(leaf []byte, parent common.Hash, parentDepth int) error {
+	root, err = s.trie.Commit(func(path []byte, leaf []byte, parent common.Hash, parentDepth int) error {
 		serializer := account.NewAccountSerializer()
 		if err := rlp.DecodeBytes(leaf, serializer); err != nil {
 			logger.Warn("RLP decode failed", "err", err, "leaf", string(leaf))
@@ -1040,10 +1040,6 @@ func (s *StateDB) Commit(deleteEmptyObjects bool) (root common.Hash, err error)
 			if pa.GetStorageRoot() != emptyState {
 				s.db.TrieDB().Reference(pa.GetStorageRoot(), parent)
 			}
-			code := common.BytesToHash(pa.GetCodeHash())
-			if code != emptyCode {
-				s.db.TrieDB().Reference(code, parent)
-			}
 		}
 		return nil
 	})
```

### blockchain/state/sync.go
```diff
@@ -34,15 +34,15 @@ import (
 // LRU cache is mendatory when state syncing and block processing are executed simultaneously
 func NewStateSync(root common.Hash, database statedb.StateTrieReadDB, bloom *statedb.SyncBloom, lruCache *lru.Cache) *statedb.TrieSync {
 	var syncer *statedb.TrieSync
-	callback := func(leaf []byte, parent common.Hash, parentDepth int) error {
+	callback := func(path []byte, leaf []byte, parent common.Hash, parentDepth int) error {
 		serializer := account.NewAccountSerializer()
 		if err := rlp.Decode(bytes.NewReader(leaf), serializer); err != nil {
 			return err
 		}
 		obj := serializer.GetAccount()
 		if pa := account.GetProgramAccount(obj); pa != nil {
-			syncer.AddSubTrie(pa.GetStorageRoot(), parentDepth+1, parent, nil)
-			syncer.AddRawEntry(common.BytesToHash(pa.GetCodeHash()), parentDepth+1, parent)
+			syncer.AddSubTrie(pa.GetStorageRoot(), path, parentDepth+1, parent, nil)
+			syncer.AddCodeEntry(common.BytesToHash(pa.GetCodeHash()), path, parentDepth+1, parent)
 		}
 		return nil
 	}
```

### blockchain/state/sync_test.go
```diff
@@ -94,9 +94,6 @@ func makeTestState(t *testing.T) (Database, common.Hash, []*testAccount) {
 	}
 	root, _ := statedb.Commit(false)
 
-	// commit stateTrie to DB
-	statedb.db.TrieDB().Commit(root, false, 0)
-
 	if err := checkStateConsistency(db.TrieDB().DiskDB(), root); err != nil {
 		t.Fatalf("inconsistent state trie at %x: %v", root, err)
 	}
@@ -216,13 +213,17 @@ func TestEmptyStateSync(t *testing.T) {
 
 // Tests that given a root hash, a state can sync iteratively on a single thread,
 // requesting retrieval tasks and returning all of them in one go.
-func TestIterativeStateSyncIndividual(t *testing.T) { testIterativeStateSync(t, 1) }
-func TestIterativeStateSyncBatched(t *testing.T)    { testIterativeStateSync(t, 100) }
+func TestIterativeStateSyncIndividual(t *testing.T)         { testIterativeStateSync(t, 1, false) }
+func TestIterativeStateSyncBatched(t *testing.T)            { testIterativeStateSync(t, 100, false) }
+func TestIterativeStateSyncIndividualFromDisk(t *testing.T) { testIterativeStateSync(t, 1, true) }
+func TestIterativeStateSyncBatchedFromDisk(t *testing.T)    { testIterativeStateSync(t, 100, true) }
 
-func testIterativeStateSync(t *testing.T, count int) {
+func testIterativeStateSync(t *testing.T, count int, commit bool) {
 	// Create a random state to copy
 	srcState, srcRoot, srcAccounts := makeTestState(t)
-
+	if commit {
+		srcState.TrieDB().Commit(srcRoot, false, 0)
+	}
 	// Create a destination state and sync with the scheduler
 	dstDiskDb := database.NewMemoryDBManager()
 	dstState := NewDatabase(dstDiskDb)
@@ -233,13 +234,18 @@ func testIterativeStateSync(t *testing.T, count int) {
 		results := make([]statedb.SyncResult, len(queue))
 		for i, hash := range queue {
 			data, err := srcState.TrieDB().Node(hash)
+			if err != nil {
+				data, err = srcState.ContractCode(hash)
+			}
 			if err != nil {
 				t.Fatalf("failed to retrieve node data for %x", hash)
 			}
 			results[i] = statedb.SyncResult{Hash: hash, Data: data}
 		}
-		if _, index, err := sched.Process(results); err != nil {
-			t.Fatalf("failed to process result #%d: %v", index, err)
+		for index, result := range results {
+			if err := sched.Process(result); err != nil {
+				t.Fatalf("failed to process result #%d: %v", index, err)
+			}
 		}
 		batch := dstDiskDb.NewBatch(database.StateTrieDB)
 		if _, err := sched.Commit(batch); err != nil {
@@ -269,8 +275,20 @@ func testIterativeStateSync(t *testing.T, count int) {
 
 func TestCheckStateConsistencyMissNode(t *testing.T) {
 	// Create a random state to copy
-	srcState, srcRoot, _ := makeTestState(t)
-	newState, _, _ := makeTestState(t)
+	srcState, srcRoot, srcAccounts := makeTestState(t)
+	newState, newRoot, _ := makeTestState(t)
+	// commit stateTrie to DB
+	srcState.TrieDB().Commit(srcRoot, false, 0)
+	newState.TrieDB().Commit(newRoot, false, 0)
+
+	isCode := func(hash common.Hash) bool {
+		for _, acc := range srcAccounts {
+			if hash == crypto.Keccak256Hash(acc.code) {
+				return true
+			}
+		}
+		return false
+	}
 
 	srcStateDB, err := New(srcRoot, srcState, nil)
 	assert.NoError(t, err)
@@ -281,12 +299,23 @@ func TestCheckStateConsistencyMissNode(t *testing.T) {
 	for it.Next() {
 		if !common.EmptyHash(it.Hash) {
 			hash := it.Hash
-			data, _ := srcStateDB.db.TrieDB().DiskDB().ReadStateTrieNode(hash[:])
-
-			// Remove nodes
-			srcState.TrieDB().DiskDB().GetMemDB().Delete(hash[:])
-			newState.TrieDB().DiskDB().GetMemDB().Delete(hash[:])
-
+			var (
+				data []byte
+				code = isCode(hash)
+				err  error
+			)
+			srcDiskDB := srcState.TrieDB().DiskDB()
+			newDiskDB := newState.TrieDB().DiskDB()
+			// Delete trie nodes or codes
+			if code {
+				data = srcDiskDB.ReadCode(hash)
+				srcState.DeleteCode(hash)
+				newState.DeleteCode(hash)
+			} else {
+				data, _ = srcDiskDB.ReadCachedTrieNode(hash)
+				srcDiskDB.GetMemDB().Delete(hash[:])
+				newDiskDB.GetMemDB().Delete(hash[:])
+			}
 			// Check consistency : errIterator
 			err = CheckStateConsistency(srcState, newState, srcRoot, 100, nil)
 			if !errors.Is(err, errIterator) {
@@ -295,8 +324,8 @@ func TestCheckStateConsistencyMissNode(t *testing.T) {
 			}
 
 			// Recover nodes
-			srcState.TrieDB().DiskDB().GetMemDB().Put(hash[:], data)
-			newState.TrieDB().DiskDB().GetMemDB().Put(hash[:], data)
+			srcDiskDB.GetMemDB().Put(hash[:], data)
+			newDiskDB.GetMemDB().Put(hash[:], data)
 		}
 	}
 
@@ -313,6 +342,7 @@ func TestCheckStateConsistencyMissNode(t *testing.T) {
 func TestIterativeDelayedStateSync(t *testing.T) {
 	// Create a random state to copy
 	srcState, srcRoot, srcAccounts := makeTestState(t)
+	srcState.TrieDB().Commit(srcRoot, false, 0)
 
 	// Create a destination state and sync with the scheduler
 	dstDiskDB := database.NewMemoryDBManager()
@@ -325,13 +355,18 @@ func TestIterativeDelayedStateSync(t *testing.T) {
 		results := make([]statedb.SyncResult, len(queue)/2+1)
 		for i, hash := range queue[:len(results)] {
 			data, err := srcState.TrieDB().Node(hash)
+			if err != nil {
+				data, err = srcState.ContractCode(hash)
+			}
 			if err != nil {
 				t.Fatalf("failed to retrieve node data for %x", hash)
 			}
 			results[i] = statedb.SyncResult{Hash: hash, Data: data}
 		}
-		if _, index, err := sched.Process(results); err != nil {
-			t.Fatalf("failed to process result #%d: %v", index, err)
+		for index, result := range results {
+			if err := sched.Process(result); err != nil {
+				t.Fatalf("failed to process result #%d: %v", index, err)
+			}
 		}
 		batch := dstDiskDB.NewBatch(database.StateTrieDB)
 		if _, err := sched.Commit(batch); err != nil {
@@ -359,6 +394,7 @@ func TestIterativeRandomStateSyncBatched(t *testing.T)    { testIterativeRandomS
 func testIterativeRandomStateSync(t *testing.T, count int) {
 	// Create a random state to copy
 	srcState, srcRoot, srcAccounts := makeTestState(t)
+	srcState.TrieDB().Commit(srcRoot, false, 0)
 
 	// Create a destination state and sync with the scheduler
 	dstDb := database.NewMemoryDBManager()
@@ -374,14 +410,19 @@ func testIterativeRandomStateSync(t *testing.T, count int) {
 		results := make([]statedb.SyncResult, 0, len(queue))
 		for hash := range queue {
 			data, err := srcState.TrieDB().Node(hash)
+			if err != nil {
+				data, err = srcState.ContractCode(hash)
+			}
 			if err != nil {
 				t.Fatalf("failed to retrieve node data for %x", hash)
 			}
 			results = append(results, statedb.SyncResult{Hash: hash, Data: data})
 		}
 		// Feed the retrieved results back and queue new tasks
-		if _, index, err := sched.Process(results); err != nil {
-			t.Fatalf("failed to process result #%d: %v", index, err)
+		for index, result := range results {
+			if err := sched.Process(result); err != nil {
+				t.Fatalf("failed to process result #%d: %v", index, err)
+			}
 		}
 		batch := dstDb.NewBatch(database.StateTrieDB)
 		if _, err := sched.Commit(batch); err != nil {
@@ -408,6 +449,7 @@ func testIterativeRandomStateSync(t *testing.T, count int) {
 func TestIterativeRandomDelayedStateSync(t *testing.T) {
 	// Create a random state to copy
 	srcState, srcRoot, srcAccounts := makeTestState(t)
+	srcState.TrieDB().Commit(srcRoot, false, 0)
 
 	// Create a destination state and sync with the scheduler
 	dstDb := database.NewMemoryDBManager()
@@ -425,6 +467,9 @@ func TestIterativeRandomDelayedStateSync(t *testing.T) {
 			delete(queue, hash)
 
 			data, err := srcState.TrieDB().Node(hash)
+			if err != nil {
+				data, err = srcState.ContractCode(hash)
+			}
 			if err != nil {
 				t.Fatalf("failed to retrieve node data for %x", hash)
 			}
@@ -435,8 +480,10 @@ func TestIterativeRandomDelayedStateSync(t *testing.T) {
 			}
 		}
 		// Feed the retrieved results back and queue new tasks
-		if _, index, err := sched.Process(results); err != nil {
-			t.Fatalf("failed to process result #%d: %v", index, err)
+		for index, result := range results {
+			if err := sched.Process(result); err != nil {
+				t.Fatalf("failed to process result #%d: %v", index, err)
+			}
 		}
 		batch := dstDb.NewBatch(database.StateTrieDB)
 		if _, err := sched.Commit(batch); err != nil {
@@ -462,7 +509,17 @@ func TestIterativeRandomDelayedStateSync(t *testing.T) {
 func TestIncompleteStateSync(t *testing.T) {
 	// Create a random state to copy
 	srcState, srcRoot, srcAccounts := makeTestState(t)
+	srcState.TrieDB().Commit(srcRoot, false, 0)
 
+	// isCode reports whether the hash is contract code hash.
+	isCode := func(hash common.Hash) bool {
+		for _, acc := range srcAccounts {
+			if hash == crypto.Keccak256Hash(acc.code) {
+				return true
+			}
+		}
+		return false
+	}
 	checkTrieConsistency(srcState.TrieDB().DiskDB().(database.DBManager), srcRoot)
 
 	// Create a destination state and sync with the scheduler
@@ -477,14 +534,19 @@ func TestIncompleteStateSync(t *testing.T) {
 		results := make([]statedb.SyncResult, len(queue))
 		for i, hash := range queue {
 			data, err := srcState.TrieDB().Node(hash)
+			if err != nil {
+				data, err = srcState.ContractCode(hash)
+			}
 			if err != nil {
 				t.Fatalf("failed to retrieve node data for %x", hash)
 			}
 			results[i] = statedb.SyncResult{Hash: hash, Data: data}
 		}
 		// Process each of the state nodes
-		if _, index, err := sched.Process(results); err != nil {
-			t.Fatalf("failed to process result #%d: %v", index, err)
+		for index, result := range results {
+			if err := sched.Process(result); err != nil {
+				t.Fatalf("failed to process result #%d: %v", index, err)
+			}
 		}
 		batch := dstDb.NewBatch(database.StateTrieDB)
 		if _, err := sched.Commit(batch); err != nil {
@@ -495,12 +557,9 @@ func TestIncompleteStateSync(t *testing.T) {
 			added = append(added, result.Hash)
 		}
 		// Check that all known sub-tries added so far are complete or missing entirely.
-	checkSubtries:
 		for _, hash := range added {
-			for _, acc := range srcAccounts {
-				if hash == crypto.Keccak256Hash(acc.code) {
-					continue checkSubtries // skip trie check of code nodes.
-				}
+			if isCode(hash) {
+				continue
 			}
 			// Can't use checkStateConsistency here because subtrie keys may have odd
 			// length and crash in LeafKey.
@@ -513,10 +572,19 @@ func TestIncompleteStateSync(t *testing.T) {
 	}
 	// Sanity check that removing any node from the database is detected
 	for _, node := range added[1:] {
-		key := node.Bytes()
-		value, _ := dstDb.GetMemDB().Get(key)
+		var (
+			key  = node.Bytes()
+			code = isCode(node)
+			val  []byte
+		)
+		if code {
+			val = dstDb.ReadCode(node)
+			dstState.DeleteCode(node)
+		} else {
+			val, _ = dstDb.ReadCachedTrieNode(node)
+			dstDb.GetMemDB().Delete(node[:])
+		}
 
-		dstDb.GetMemDB().Delete(key)
 		if err := checkStateConsistency(dstDb, added[0]); err == nil {
 			t.Fatalf("trie inconsistency not caught, missing: %x", key)
 		}
@@ -526,8 +594,12 @@ func TestIncompleteStateSync(t *testing.T) {
 
 		err = CheckStateConsistencyParallel(srcState, dstState, srcRoot, nil)
 		assert.Error(t, err)
-
-		dstDb.GetMemDB().Put(key, value)
+		if code {
+			dstDb.WriteCode(node, val)
+		} else {
+			// insert a trie node to memory database
+			dstDb.GetMemDB().Put(node[:], val)
+		}
 	}
 
 	err := CheckStateConsistency(srcState, dstState, srcRoot, 100, nil)
```

### blockchain/state_migration.go
```diff
@@ -62,6 +62,10 @@ func (td *stateTrieMigrationDB) HasStateTrieNode(key []byte) (bool, error) {
 	return td.HasStateTrieNodeFromNew(key)
 }
 
+func (td *stateTrieMigrationDB) HasCodeWithPrefix(hash common.Hash) bool {
+	return td.HasCodeWithPrefixFromNew(hash)
+}
+
 func (td *stateTrieMigrationDB) ReadPreimage(hash common.Hash) []byte {
 	return td.ReadPreimageFromNew(hash)
 }
@@ -82,13 +86,16 @@ func (bc *BlockChain) stateMigrationCommit(s *statedb.TrieSync, batch database.B
 	return written, nil
 }
 
-func (bc *BlockChain) concurrentRead(db *statedb.Database, quitCh chan struct{}, hashCh chan common.Hash, resultCh chan statedb.SyncResult) {
+func (bc *BlockChain) concurrentRead(db state.Database, quitCh chan struct{}, hashCh chan common.Hash, resultCh chan statedb.SyncResult) {
 	for {
 		select {
 		case <-quitCh:
 			return
 		case hash := <-hashCh:
-			data, err := db.NodeFromOld(hash)
+			data, err := db.TrieDB().NodeFromOld(hash)
+			if err != nil {
+				data, err = db.ContractCode(hash)
+			}
 			if err != nil {
 				resultCh <- statedb.SyncResult{Hash: hash, Err: err}
 				continue
@@ -136,7 +143,7 @@ func (bc *BlockChain) migrateState(rootHash common.Hash) (returnErr error) {
 	resultCh := make(chan statedb.SyncResult, threads)
 
 	for th := 0; th < threads; th++ {
-		go bc.concurrentRead(srcState.TrieDB(), quitCh, hashCh, resultCh)
+		go bc.concurrentRead(srcState, quitCh, hashCh, resultCh)
 	}
 
 	stateTrieBatch := dstState.TrieDB().DiskDB().NewBatch(database.StateTrieDB)
@@ -169,9 +176,11 @@ func (bc *BlockChain) migrateState(rootHash common.Hash) (returnErr error) {
 
 		// Process trie nodes
 		startProcess := time.Now()
-		if _, index, err := trieSync.Process(results); err != nil {
-			logger.Error("State migration is failed by process error", "err", err)
-			return fmt.Errorf("failed to process result #%d: %v", index, err)
+		for index, result := range results {
+			if err := trieSync.Process(result); err != nil {
+				logger.Error("State migration is failed by process error", "err", err)
+				return fmt.Errorf("failed to process result #%d: %v", index, err)
+			}
 		}
 		stats.processElapsed += time.Since(startProcess)
 
```

### blockchain/tx_list.go
```diff
@@ -310,9 +310,10 @@ func (l *txList) Forward(threshold uint64) types.Transactions {
 // a point in calculating all the costs or if the balance covers all. If the threshold
 // is lower than the costcap, the caps will be reset to a new high after removing
 // the newly invalidated transactions.
-func (l *txList) Filter(senderBalance *big.Int, pool *TxPool) (types.Transactions, types.Transactions) {
+func (l *txList) Filter(sender common.Address, pool *TxPool) (types.Transactions, types.Transactions) {
 	// Filter out all the transactions above the account's funds
 	removed := l.txs.Filter(func(tx *types.Transaction) bool {
+		senderBalance := pool.getBalance(sender)
 		// Drop a tx if it is marked as un-executable on block generation process.
 		if tx.IsMarkedUnexecutable() {
 			return true
@@ -326,6 +327,11 @@ func (l *txList) Filter(senderBalance *big.Int, pool *TxPool) (types.Transaction
 			feePayer, _ := tx.FeePayer()
 			feePayerBalance := pool.getBalance(feePayer)
 			feeRatio, isRatioTx := tx.FeeRatio()
+
+			// Handling the special case when the sender and fee payer are the same.
+			if sender == feePayer {
+				return senderBalance.Cmp(tx.Cost()) < 0
+			}
 			if isRatioTx {
 				feeByFeePayer, feeBySender := types.CalcFeeWithRatio(feeRatio, tx.Fee())
 				return senderBalance.Cmp(new(big.Int).Add(tx.Value(), feeBySender)) < 0 || feePayerBalance.Cmp(feeByFeePayer) < 0
```

### blockchain/tx_pool.go
```diff
@@ -739,6 +739,13 @@ func (pool *TxPool) validateTx(tx *types.Transaction) error {
 				return ErrInsufficientFundsFeePayer
 			}
 		}
+		// additional balance check in case of sender = feepayer
+		// since a single account has to bear the both cost(feepayer_cost + sender_cost),
+		// it is necessary to check whether the balance is equal to the sum of the cost.
+		if from == feePayer && senderBalance.Cmp(tx.Cost()) < 0 {
+			logger.Trace("[tx_pool] insufficient funds for cost(gas * price + value)", "from", from, "balance", senderBalance, "cost", tx.Cost())
+			return ErrInsufficientFundsFrom
+		}
 	} else {
 		// balance check for non-fee-delegated tx
 		if senderBalance.Cmp(tx.Cost()) < 0 {
@@ -1330,7 +1337,7 @@ func (pool *TxPool) promoteExecutables(accounts []common.Address) {
 			pool.priced.Removed()
 		}
 		// Drop all transactions that are too costly (low balance)
-		drops, _ := list.Filter(pool.getBalance(addr), pool)
+		drops, _ := list.Filter(addr, pool)
 		for _, tx := range drops {
 			hash := tx.Hash()
 			logger.Trace("Removed unpayable queued transaction", "hash", hash)
@@ -1503,7 +1510,7 @@ func (pool *TxPool) demoteUnexecutables() {
 		// The logic below loosely checks the tx count for the efficiency and the simplicity.
 		if cnt < demoteUnexecutablesFullValidationTxLimit {
 			cnt += list.Len()
-			drops, invalids = list.Filter(pool.getBalance(addr), pool)
+			drops, invalids = list.Filter(addr, pool)
 		} else {
 			drops, invalids = list.FilterUnexecutable()
 		}
```
