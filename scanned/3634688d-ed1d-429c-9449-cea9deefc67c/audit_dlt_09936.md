# [?] Merge pull request from GHSA-4vx6-m7jv-g2ch

## Summary
Severity: Unknown
Chain: Kaia
Component: kaiachain/kaia
Published: 2022-11-22
Source: https://github.com/kaiachain/kaia/commit/25804bd24c4875398512b2857fedb7d8e063d8f5
Type: security-commit

## Details
Merge pull request from GHSA-4vx6-m7jv-g2ch

Fix debug namespace API

## Patch
### api/api_private_debug.go
```diff
@@ -21,9 +21,11 @@
 package api
 
 import (
+	"context"
 	"fmt"
 	"strings"
 
+	"github.com/davecgh/go-spew/spew"
 	"github.com/klaytn/klaytn/networks/rpc"
 	"github.com/syndtr/goleveldb/leveldb"
 	"github.com/syndtr/goleveldb/leveldb/util"
@@ -84,3 +86,13 @@ func (api *PrivateDebugAPI) SetHead(number rpc.BlockNumber) {
 	}
 	api.b.SetHead(uint64(number))
 }
+
+// PrintBlock retrieves a block and returns its pretty printed form.
+func (api *PrivateDebugAPI) PrintBlock(ctx context.Context, blockNrOrHash rpc.BlockNumberOrHash) (string, error) {
+	block, _ := api.b.BlockByNumberOrHash(ctx, blockNrOrHash)
+	if block == nil {
+		blockNumberOrHashString, _ := blockNrOrHash.NumberOrHashString()
+		return "", fmt.Errorf("block %v not found", blockNumberOrHashString)
+	}
+	return spew.Sdump(block), nil
+}
```

### api/api_public_debug.go
```diff
@@ -24,7 +24,6 @@ import (
 	"context"
 	"fmt"
 
-	"github.com/davecgh/go-spew/spew"
 	"github.com/klaytn/klaytn/networks/rpc"
 	"github.com/klaytn/klaytn/rlp"
 )
@@ -54,13 +53,3 @@ func (api *PublicDebugAPI) GetBlockRlp(ctx context.Context, blockNrOrHash rpc.Bl
 	}
 	return fmt.Sprintf("%x", encoded), nil
 }
-
-// PrintBlock retrieves a block and returns its pretty printed form.
-func (api *PublicDebugAPI) PrintBlock(ctx context.Context, blockNrOrHash rpc.BlockNumberOrHash) (string, error) {
-	block, _ := api.b.BlockByNumberOrHash(ctx, blockNrOrHash)
-	if block == nil {
-		blockNumberOrHashString, _ := blockNrOrHash.NumberOrHashString()
-		return "", fmt.Errorf("block %v not found", blockNumberOrHashString)
-	}
-	return spew.Sdump(block), nil
-}
```

### api/backend.go
```diff
@@ -135,11 +135,12 @@ func GetAPIs(apiBackend Backend) ([]rpc.API, *EthereumAPI) {
 			Namespace: "debug",
 			Version:   "1.0",
 			Service:   NewPublicDebugAPI(apiBackend),
-			Public:    true,
+			Public:    false,
 		}, {
-			Namespace: "debug",
+			Namespace: "unsafedebug",
 			Version:   "1.0",
 			Service:   NewPrivateDebugAPI(apiBackend),
+			Public:    false,
 		}, {
 			Namespace: "klay",
 			Version:   "1.0",
```

### console/web3ext/web3ext.go
```diff
@@ -23,6 +23,7 @@ package web3ext
 var Modules = map[string]string{
 	"admin":            Admin_JS,
 	"debug":            Debug_JS,
+	"unsafedebug":      UnsafeDebug_JS,
 	"klay":             Klay_JS,
 	"net":              Net_JS,
 	"personal":         Personal_JS,
@@ -341,7 +342,7 @@ web3._extend({
 		new web3._extend.Property({
 			name: 'chainConfig',
 			getter: 'governance_chainConfig',
-		}),	
+		}),
 		new web3._extend.Property({
 			name: 'nodeAddress',
 			getter: 'governance_nodeAddress',
@@ -508,8 +509,13 @@ web3._extend({
 	property: 'debug',
 	methods: [
 		new web3._extend.Method({
-			name: 'printBlock',
-			call: 'debug_printBlock',
+			name: 'dumpBlock',
+			call: 'debug_dumpBlock',
+			params: 1
+		}),
+		new web3._extend.Method({
+			name: 'dumpStateTrie',
+			call: 'debug_dumpStateTrie',
 			params: 1
 		}),
 		new web3._extend.Method({
@@ -518,277 +524,317 @@ web3._extend({
 			params: 1
 		}),
 		new web3._extend.Method({
-			name: 'setHead',
-			call: 'debug_setHead',
+			name: 'getModifiedAccountsByNumber',
+			call: 'debug_getModifiedAccountsByNumber',
+			params: 2,
+			inputFormatter: [null, null],
+		}),
+		new web3._extend.Method({
+			name: 'getModifiedAccountsByHash',
+			call: 'debug_getModifiedAccountsByHash',
+			params: 2,
+			inputFormatter:[null, null],
+		}),
+		new web3._extend.Method({
+			name: 'getModifiedStorageNodesByNumber',
+			call: 'debug_getModifiedStorageNodesByNumber',
+			params: 4,
+			inputFormatter: [null, null, null, null],
+		}),
+		new web3._extend.Method({
+			name: 'getBadBlocks',
+			call: 'debug_getBadBlocks',
+			params: 0,
+		}),
+		new web3._extend.Method({
+			name: 'traceBlock',
+			call: 'debug_traceBlock',
+			params: 2,
+			inputFormatter: [null, null]
+		}),
+		new web3._extend.Method({
+			name: 'traceBadBlock',
+			call: 'debug_traceBadBlock',
 			params: 1,
-			inputFormatter: [web3._extend.formatters.inputBlockNumberFormatter]
+			inputFormatter: [null]
 		}),
 		new web3._extend.Method({
-			name: 'dumpBlock',
-			call: 'debug_dumpBlock',
-			params: 1
+			name: 'traceBlockByNumber',
+			call: 'debug_traceBlockByNumber',
+			params: 2,
+			inputFormatter: [web3._extend.formatters.inputBlockNumberFormatter, null]
 		}),
 		new web3._extend.Method({
-			name: 'dumpStateTrie',
-			call: 'debug_dumpStateTrie',
+			name: 'traceBlockByNumberRange',
+			call: 'debug_traceBlockByNumberRange',
+			params: 3,
+			inputFormatter: [web3._extend.formatters.inputBlockNumberFormatter, web3._extend.formatters.inputBlockNumberFormatter, null]
+		}),
+		new web3._extend.Method({
+			name: 'traceBlockByHash',
+			call: 'debug_traceBlockByHash',
+			params: 2,
+			inputFormatter: [null, null]
+		}),
+		new web3._extend.Method({
+			name: 'traceTransaction',
+			call: 'debug_traceTransaction',
+			params: 2,
+			inputFormatter: [null, null]
+		}),
+	],
+	properties: []
+});
+`
+
+const UnsafeDebug_JS = `
+web3._extend({
+	property: 'unsafedebug',
+	methods: [
+		new web3._extend.Method({
+			name: 'printBlock',
+			call: 'unsafedebug_printBlock',
 			params: 1
 		}),
+		new web3._extend.Method({
+			name: 'setHead',
+			call: 'unsafedebug_setHead',
+			params: 1,
+			inputFormatter: [web3._extend.formatters.inputBlockNumberFormatter]
+		}),
 		new web3._extend.Method({
 			name: 'startWarmUp',
-			call: 'debug_startWarmUp',
+			call: 'unsafedebug_startWarmUp',
 		}),
 		new web3._extend.Method({
 			name: 'startContractWarmUp',
-			call: 'debug_startContractWarmUp',
+			call: 'unsafedebug_startContractWarmUp',
 			params: 1
 		}),
 		new web3._extend.Method({
 			name: 'stopWarmUp',
-			call: 'debug_stopWarmUp',
+			call: 'unsafedebug_stopWarmUp',
 		}),
 		new web3._extend.Method({
 			name: 'startCollectingTrieStats',
-			call: 'debug_startCollectingTrieStats',
+			call: 'unsafedebug_startCollectingTrieStats',
 			params: 1,
 		}),
 		new web3._extend.Method({
 			name: 'chaindbProperty',
-			call: 'debug_chaindbProperty',
+			call: 'unsafedebug_chaindbProperty',
 			params: 1,
 			outputFormatter: console.log
 		}),
 		new web3._extend.Method({
 			name: 'chaindbCompact',
-			call: 'debug_chaindbCompact',
+			call: 'unsafedebug_chaindbCompact',
 		}),
 		new web3._extend.Method({
 			name: 'metrics',
-			call: 'debug_metrics',
+			call: 'unsafedebug_metrics',
 			params: 1
 		}),
 		new web3._extend.Method({
 			name: 'verbosity',
-			call: 'debug_verbosity',
+			call: 'unsafedebug_verbosity',
 			params: 1
 		}),
 		new web3._extend.Method({
 			name: 'verbosityByName',
-			call: 'debug_verbosityByName',
+			call: 'unsafedebug_verbosityByName',
 			params: 2
 		}),
 		new web3._extend.Method({
 			name: 'verbosityByID',
-			call: 'debug_verbosityByID',
+			call: 'unsafedebug_verbosityByID',
 			params: 2
 		}),
 		new web3._extend.Method({
 			name: 'vmodule',
-			call: 'debug_vmodule',
+			call: 'unsafedebug_vmodule',
 			params: 1
 		}),
 		new web3._extend.Method({
 			name: 'backtraceAt',
-			call: 'debug_backtraceAt',
+			call: 'unsafedebug_backtraceAt',
 			params: 1,
 		}),
 		new web3._extend.Method({
 			name: 'stacks',
-			call: 'debug_stacks',
+			call: 'unsafedebug_stacks',
 			params: 0,
 			outputFormatter: console.log
 		}),
 		new web3._extend.Method({
 			name: 'freeOSMemory',
-			call: 'debug_freeOSMemory',
+			call: 'unsafedebug_freeOSMemory',
 			params: 0,
 		}),
 		new web3._extend.Method({
 			name: 'setGCPercent',
-			call: 'debug_setGCPercent',
+			call: 'unsafedebug_setGCPercent',
 			params: 1,
 		}),
 		new web3._extend.Method({
 			name: 'memStats',
-			call: 'debug_memStats',
+			call: 'unsafedebug_memStats',
 			params: 0,
 		}),
 		new web3._extend.Method({
 			name: 'gcStats',
-			call: 'debug_gcStats',
+			call: 'unsafedebug_gcStats',
 			params: 0,
 		}),
 		new web3._extend.Method({
 			name: 'startPProf',
-			call: 'debug_startPProf',
+			call: 'unsafedebug_startPProf',
 			params: 2,
 			inputFormatter: [null, null]
 		}),
 		new web3._extend.Method({
 			name: 'stopPProf',
-			call: 'debug_stopPProf',
+			call: 'unsafedebug_stopPProf',
 			params: 0
 		}),
 		new web3._extend.Method({
 			name: 'isPProfRunning',
-			call: 'debug_isPProfRunning',
+			call: 'unsafedebug_isPProfRunning',
 			params: 0
 		}),
 		new web3._extend.Method({
 			name: 'cpuProfile',
-			call: 'debug_cpuProfile',
+			call: 'unsafedebug_cpuProfile',
 			params: 2
 		}),
 		new web3._extend.Method({
 			name: 'startCPUProfile',
-			call: 'debug_startCPUProfile',
+			call: 'unsafedebug_startCPUProfile',
 			params: 1
 		}),
 		new web3._extend.Method({
 			name: 'stopCPUProfile',
-			call: 'debug_stopCPUProfile',
+			call: 'unsafedebug_stopCPUProfile',
 			params: 0
 		}),
 		new web3._extend.Method({
 			name: 'goTrace',
-			call: 'debug_goTrace',
+			call: 'unsafedebug_goTrace',
 			params: 2
 		}),
 		new web3._extend.Method({
 			name: 'startGoTrace',
-			call: 'debug_startGoTrace',
+			call: 'unsafedebug_startGoTrace',
 			params: 1
 		}),
 		new web3._extend.Method({
 			name: 'stopGoTrace',
-			call: 'debug_stopGoTrace',
+			call: 'unsafedebug_stopGoTrace',
 			params: 0
 		}),
 		new web3._extend.Method({
 			name: 'blockProfile',
-			call: 'debug_blockProfile',
+			call: 'unsafedebug_blockProfile',
 			params: 2
 		}),
 		new web3._extend.Method({
 			name: 'setBlockProfileRate',
-			call: 'debug_setBlockProfileRate',
+			call: 'unsafedebug_setBlockProfileRate',
 			params: 1
 		}),
 		new web3._extend.Method({
 			name: 'writeBlockProfile',
-			call: 'debug_writeBlockProfile',
+			call: 'unsafedebug_writeBlockProfile',
 			params: 1
 		}),
 		new web3._extend.Method({
 			name: 'mutexProfile',
-			call: 'debug_mutexProfile',
+			call: 'unsafedebug_mutexProfile',
 			params: 2
 		}),
 		new web3._extend.Method({
 			name: 'setMutexProfileRate',
-			call: 'debug_setMutexProfileRate',
+			call: 'unsafedebug_setMutexProfileRate',
 			params: 1
 		}),
 		new web3._extend.Method({
 			name: 'writeMutexProfile',
-			call: 'debug_writeMutexProfile',
+			call: 'unsafedebug_writeMutexProfile',
 			params: 1
 		}),
 		new web3._extend.Method({
 			name: 'writeMemProfile',
-			call: 'debug_writeMemProfile',
+			call: 'unsafedebug_writeMemProfile',
 			params: 1
 		}),
 		new web3._extend.Method({
 			name: 'traceBlock',
-			call: 'debug_traceBlock',
+			call: 'unsafedebug_traceBlock',
 			params: 2,
 			inputFormatter: [null, null]
 		}),
 		new web3._extend.Method({
 			name: 'traceBlockFromFile',
-			call: 'debug_traceBlockFromFile',
+			call: 'unsafedebug_traceBlockFromFile',
 			params: 2,
 			inputFormatter: [null, null]
 		}),
 		new web3._extend.Method({
 			name: 'traceBadBlock',
-			call: 'debug_traceBadBlock',
+			call: 'unsafedebug_traceBadBlock',
 			params: 1,
 			inputFormatter: [null]
 		}),
 		new web3._extend.Method({
 			name: 'standardTraceBadBlockToFile',
-			call: 'debug_standardTraceBadBlockToFile',
+			call: 'unsafedebug_standardTraceBadBlockToFile',
 			params: 2,
 			inputFormatter: [null, null]
 		}),
 		new web3._extend.Method({
 			name: 'standardTraceBlockToFile',
-			call: 'debug_standardTraceBlockToFile',
+			call: 'unsafedebug_standardTraceBlockToFile',
 			params: 2,
 			inputFormatter: [null, null]
 		}),
 		new web3._extend.Method({
 			name: 'traceBlockByNumber',
-			call: 'debug_traceBlockByNumber',
+			call: 'unsafedebug_traceBlockByNumber',
 			params: 2,
 			inputFormatter: [web3._extend.formatters.inputBlockNumberFormatter, null]
 		}),
 		new web3._extend.Method({
 			name: 'traceBlockByNumberRange',
-			call: 'debug_traceBlockByNumberRange',
+			call: 'unsafedebug_traceBlockByNumberRange',
 			params: 3,
 			inputFormatter: [web3._extend.formatters.inputBlockNumberFormatter, web3._extend.formatters.inputBlockNumberFormatter, null]
 		}),
 		new web3._extend.Method({
 			name: 'traceBlockByHash',
-			call: 'debug_traceBlockByHash',
+			call: 'unsafedebug_traceBlockByHash',
 			params: 2,
 			inputFormatter: [null, null]
 		}),
 		new web3._extend.Method({
 			name: 'traceTransaction',
-			call: 'debug_traceTransaction',
+			call: 'unsafedebug_traceTransaction',
 			params: 2,
 			inputFormatter: [null, null]
 		}),
 		new web3._extend.Method({
 			name: 'preimage',
-			call: 'debug_preimage',
+			call: 'unsafedebug_preimage',
 			params: 1,
 			inputFormatter: [null]
 		}),
-		new web3._extend.Method({
-			name: 'getBadBlocks',
-			call: 'debug_getBadBlocks',
-			params: 0,
-		}),
 		new web3._extend.Method({
 			name: 'storageRangeAt',
-			call: 'debug_storageRangeAt',
+			call: 'unsafedebug_storageRangeAt',
 			params: 5,
 		}),
-		new web3._extend.Method({
-			name: 'getModifiedAccountsByNumber',
-			call: 'debug_getModifiedAccountsByNumber',
-			params: 2,
-			inputFormatter: [null, null],
-		}),
-		new web3._extend.Method({
-			name: 'getModifiedAccountsByHash',
-			call: 'debug_getModifiedAccountsByHash',
-			params: 2,
-			inputFormatter:[null, null],
-		}),
-		new web3._extend.Method({
-			name: 'getModifiedStorageNodesByNumber',
-			call: 'debug_getModifiedStorageNodesByNumber',
-			params: 4,
-			inputFormatter: [null, null, null, null],
-		}),
 		new web3._extend.Method({
 			name: 'setVMLogTarget',
-			call: 'debug_setVMLogTarget',
+			call: 'unsafedebug_setVMLogTarget',
 			params: 1
 		}),
 	],
```

### node/cn/api.go
```diff
@@ -343,24 +343,28 @@ func (api *PublicDebugAPI) DumpStateTrie(ctx context.Context, blockNrOrHash rpc.
 	return result, nil
 }
 
+// TODO-klaytn: Rearrange PublicDebugAPI and PrivateDebugAPI receivers
 // StartWarmUp retrieves all state/storage tries of the latest committed state root and caches the tries.
-func (api *PublicDebugAPI) StartWarmUp() error {
+func (api *PrivateDebugAPI) StartWarmUp() error {
 	return api.cn.blockchain.StartWarmUp()
 }
 
+// TODO-klaytn: Rearrange PublicDebugAPI and PrivateDebugAPI receivers
 // StartContractWarmUp retrieves a storage trie of the latest state root and caches the trie
 // corresponding to the given contract address.
-func (api *PublicDebugAPI) StartContractWarmUp(contractAddr common.Address) error {
+func (api *PrivateDebugAPI) StartContractWarmUp(contractAddr common.Address) error {
 	return api.cn.blockchain.StartContractWarmUp(contractAddr)
 }
 
+// TODO-klaytn: Rearrange PublicDebugAPI and PrivateDebugAPI receivers
 // StopWarmUp stops the warming up process.
-func (api *PublicDebugAPI) StopWarmUp() error {
+func (api *PrivateDebugAPI) StopWarmUp() error {
 	return api.cn.blockchain.StopWarmUp()
 }
 
+// TODO-klaytn: Rearrange PublicDebugAPI and PrivateDebugAPI receivers
 // StartCollectingTrieStats  collects state/storage trie statistics and print in the log.
-func (api *PublicDebugAPI) StartCollectingTrieStats(contractAddr common.Address) error {
+func (api *PrivateDebugAPI) StartCollectingTrieStats(contractAddr common.Address) error {
 	return api.cn.blockchain.StartCollectingTrieStats(contractAddr)
 }
 
@@ -385,9 +389,10 @@ func (api *PrivateDebugAPI) Preimage(ctx context.Context, hash common.Hash) (hex
 	return nil, errors.New("unknown preimage")
 }
 
+// TODO-klaytn: Rearrange PublicDebugAPI and PrivateDebugAPI receivers
 // GetBadBLocks returns a list of the last 'bad blocks' that the client has seen on the network
 // and returns them as a JSON list of block-hashes
-func (api *PrivateDebugAPI) GetBadBlocks(ctx context.Context) ([]blockchain.BadBlockArgs, error) {
+func (api *PublicDebugAPI) GetBadBlocks(ctx context.Context) ([]blockchain.BadBlockArgs, error) {
 	return api.cn.BlockChain().BadBlocks()
 }
 
@@ -445,25 +450,27 @@ func storageRangeAt(st state.Trie, start []byte, maxResult int) (StorageRangeRes
 	return result, nil
 }
 
+// TODO-klaytn: Rearrange PublicDebugAPI and PrivateDebugAPI receivers
 // GetModifiedAccountsByNumber returns all accounts that have changed between the
 // two blocks specified. A change is defined as a difference in nonce, balance,
 // code hash, or storage hash.
 //
 // With one parameter, returns the list of accounts modified in the specified block.
-func (api *PrivateDebugAPI) GetModifiedAccountsByNumber(ctx context.Context, startNum rpc.BlockNumber, endNum *rpc.BlockNumber) ([]common.Address, error) {
+func (api *PublicDebugAPI) GetModifiedAccountsByNumber(ctx context.Context, startNum rpc.BlockNumber, endNum *rpc.BlockNumber) ([]common.Address, error) {
 	startBlock, endBlock, err := api.getStartAndEndBlock(ctx, startNum, endNum)
 	if err != nil {
 		return nil, err
 	}
 	return api.getModifiedAccounts(startBlock, endBlock)
 }
 
+// TODO-klaytn: Rearrange PublicDebugAPI and PrivateDebugAPI receivers
 // GetModifiedAccountsByHash returns all accounts that have changed between the
 // two blocks specified. A change is defined as a difference in nonce, balance,
 // code hash, or storage hash.
 //
 // With one parameter, returns the list of accounts modified in the specified block.
-func (api *PrivateDebugAPI) GetModifiedAccountsByHash(startHash common.Hash, endHash *common.Hash) ([]common.Address, error) {
+func (api *PublicDebugAPI) GetModifiedAccountsByHash(startHash common.Hash, endHash *common.Hash) ([]common.Address, error) {
 	var startBlock, endBlock *types.Block
 	startBlock = api.cn.blockchain.GetBlockByHash(startHash)
 	if startBlock == nil {
@@ -485,7 +492,8 @@ func (api *PrivateDebugAPI) GetModifiedAccountsByHash(startHash common.Hash, end
 	return api.getModifiedAccounts(startBlock, endBlock)
 }
 
-func (api *PrivateDebugAPI) getModifiedAccounts(startBlock, endBlock *types.Block) ([]common.Address, error) {
+// TODO-klaytn: Rearrange PublicDebugAPI and PrivateDebugAPI receivers
+func (api *PublicDebugAPI) getModifiedAccounts(startBlock, endBlock *types.Block) ([]common.Address, error) {
 	trieDB := api.cn.blockchain.StateCache().TrieDB()
 
 	oldTrie, err := statedb.NewSecureTrie(startBlock.Root(), trieDB)
@@ -511,8 +519,9 @@ func (api *PrivateDebugAPI) getModifiedAccounts(startBlock, endBlock *types.Bloc
 	return dirty, nil
 }
 
+// TODO-klaytn: Rearrange PublicDebugAPI and PrivateDebugAPI receivers
 // getStartAndEndBlock returns start and end block based on the given startNum and endNum.
-func (api *PrivateDebugAPI) getStartAndEndBlock(ctx context.Context, startNum rpc.BlockNumber, endNum *rpc.BlockNumber) (*types.Block, *types.Block, error) {
+func (api *PublicDebugAPI) getStartAndEndBlock(ctx context.Context, startNum rpc.BlockNumber, endNum *rpc.BlockNumber) (*types.Block, *types.Block, error) {
 	var startBlock, endBlock *types.Block
 
 	startBlock, err := api.cn.APIBackend.BlockByNumber(ctx, startNum)
@@ -540,19 +549,21 @@ func (api *PrivateDebugAPI) getStartAndEndBlock(ctx context.Context, startNum rp
 	return startBlock, endBlock, nil
 }
 
+// TODO-klaytn: Rearrange PublicDebugAPI and PrivateDebugAPI receivers
 // GetModifiedStorageNodesByNumber returns the number of storage nodes of a contract account
 // that have been changed between the two blocks specified.
 //
 // With the first two parameters, it returns the number of storage trie nodes modified in the specified block.
-func (api *PrivateDebugAPI) GetModifiedStorageNodesByNumber(ctx context.Context, contractAddr common.Address, startNum rpc.BlockNumber, endNum *rpc.BlockNumber, printDetail *bool) (int, error) {
+func (api *PublicDebugAPI) GetModifiedStorageNodesByNumber(ctx context.Context, contractAddr common.Address, startNum rpc.BlockNumber, endNum *rpc.BlockNumber, printDetail *bool) (int, error) {
 	startBlock, endBlock, err := api.getStartAndEndBlock(ctx, startNum, endNum)
 	if err != nil {
 		return 0, err
 	}
 	return api.getModifiedStorageNodes(contractAddr, startBlock, endBlock, printDetail)
 }
 
-func (api *PrivateDebugAPI) getModifiedStorageNodes(contractAddr common.Address, startBlock, endBlock *types.Block, printDetail *bool) (int, error) {
+// TODO-klaytn: Rearrange PublicDebugAPI and PrivateDebugAPI receivers
+func (api *PublicDebugAPI) getModifiedStorageNodes(contractAddr common.Address, startBlock, endBlock *types.Block, printDetail *bool) (int, error) {
 	startBlockRoot, err := api.cn.blockchain.GetContractStorageRoot(startBlock, api.cn.blockchain.StateCache(), contractAddr)
 	if err != nil {
 		return 0, err
```

### node/cn/backend.go
```diff
@@ -487,7 +487,8 @@ func (s *CN) APIs() []rpc.API {
 	governanceKlayAPI := governance.NewGovernanceKlayAPI(s.governance, s.blockchain)
 	publicGovernanceAPI := governance.NewGovernanceAPI(s.governance)
 	publicDownloaderAPI := downloader.NewPublicDownloaderAPI(s.protocolManager.Downloader(), s.eventMux)
-	privateTracerAPI := tracers.NewAPI(s.APIBackend)
+	tracerAPI := tracers.NewAPI(s.APIBackend)
+	unsafeTracerAPI := tracers.NewUnsafeAPI(s.APIBackend)
 
 	ethAPI.SetPublicFilterAPI(publicFilterAPI)
 	ethAPI.SetGovernanceKlayAPI(governanceKlayAPI)
@@ -523,15 +524,21 @@ func (s *CN) APIs() []rpc.API {
 			Namespace: "debug",
 			Version:   "1.0",
 			Service:   NewPublicDebugAPI(s),
-			Public:    true,
+			Public:    false,
 		}, {
-			Namespace: "debug",
+			Namespace: "unsafedebug",
 			Version:   "1.0",
 			Service:   NewPrivateDebugAPI(s.chainConfig, s),
+			Public:    false,
 		}, {
 			Namespace: "debug",
 			Version:   "1.0",
-			Service:   privateTracerAPI,
+			Service:   tracerAPI,
+			Public:    false,
+		}, {
+			Namespace: "unsafedebug",
+			Version:   "1.0",
+			Service:   unsafeTracerAPI,
 			Public:    false,
 		}, {
 			Namespace: "net",
```

### node/cn/tracers/api.go
```diff
@@ -92,12 +92,20 @@ type Backend interface {
 
 // API is the collection of tracing APIs exposed over the private debugging endpoint.
 type API struct {
-	backend Backend
+	backend     Backend
+	unsafeTrace bool
 }
 
-// NewAPI creates a new API definition for the tracing methods of the CN service.
+// NewAPI creates a new API definition for the tracing methods of the CN service,
+// only allowing predefined tracers.
 func NewAPI(backend Backend) *API {
-	return &API{backend: backend}
+	return &API{backend: backend, unsafeTrace: false}
+}
+
+// NewUnsafeAPI creates a new API definition for the tracing methods of the CN service,
+// allowing both predefined tracers and Javascript snippet based tracing.
+func NewUnsafeAPI(backend Backend) *API {
+	return &API{backend: backend, unsafeTrace: true}
 }
 
 type chainContext struct {
@@ -492,6 +500,9 @@ func (api *API) TraceBlock(ctx context.Context, blob hexutil.Bytes, config *Trac
 // TraceBlockFromFile returns the structured logs created during the execution of
 // EVM and returns them as a JSON object.
 func (api *API) TraceBlockFromFile(ctx context.Context, file string, config *TraceConfig) ([]*txTraceResult, error) {
+	if !api.unsafeTrace {
+		return nil, errors.New("TraceBlockFromFile is not supported in 'debug' namespace, use 'unsafedebug' namespace instead")
+	}
 	blob, err := ioutil.ReadFile(file)
 	if err != nil {
 		return nil, fmt.Errorf("could not read file: %v", err)
@@ -793,8 +804,8 @@ func (api *API) traceTx(ctx context.Context, message blockchain.Message, vmctx v
 		if *config.Tracer == fastCallTracer {
 			tracer = vm.NewInternalTxTracer()
 		} else {
-			// Constuct the JavaScript tracer to execute with
-			if tracer, err = New(*config.Tracer); err != nil {
+			// Construct the JavaScript tracer to execute with
+			if tracer, err = New(*config.Tracer, api.unsafeTrace); err != nil {
 				return nil, err
 			}
 		}
```

### node/cn/tracers/tracer.go
```diff
@@ -317,13 +317,18 @@ type Tracer struct {
 	reason    error  // Textual reason for the interruption
 }
 
-// New instantiates a new tracer instance. code specifies a Javascript snippet,
-// which must evaluate to an expression returning an object with 'step', 'fault'
-// and 'result' functions.
-func New(code string) (*Tracer, error) {
+// New instantiates a new tracer instance. code specifies either a predefined
+// tracer name or a Javascript snippet, which must evaluate to an expression
+// returning an object with 'step', 'fault' and 'result' functions.
+// However, if unsafeTrace is false, code should specify predefined tracer name,
+// otherwise error is returned.
+func New(code string, unsafeTrace bool) (*Tracer, error) {
 	// Resolve any tracers by name and assemble the tracer object
-	if tracer, ok := tracer(code); ok {
-		code = tracer
+	foundTracer, ok := tracer(code)
+	if ok {
+		code = foundTracer
+	} else if !unsafeTrace {
+		return nil, fmt.Errorf("Only predefined tracers are supported")
 	}
 	tracer := &Tracer{
 		vm:              duktape.New(),
```

### node/cn/tracers/tracer_test.go
```diff
@@ -71,7 +71,7 @@ func runTrace(tracer *Tracer) (json.RawMessage, error) {
 
 // TestRegressionPanicSlice tests that we don't panic on bad arguments to memory access
 func TestRegressionPanicSlice(t *testing.T) {
-	tracer, err := New("{depths: [], step: function(log) { this.depths.push(log.memory.slice(-1,-2)); }, fault: function() {}, result: function() { return this.depths; }}")
+	tracer, err := New("{depths: [], step: function(log) { this.depths.push(log.memory.slice(-1,-2)); }, fault: function() {}, result: function() { return this.depths; }}", true)
 	if err != nil {
 		t.Fatal(err)
 	}
@@ -82,7 +82,7 @@ func TestRegressionPanicSlice(t *testing.T) {
 
 // TestRegressionPanicSlice tests that we don't panic on bad arguments to stack peeks
 func TestRegressionPanicPeek(t *testing.T) {
-	tracer, err := New("{depths: [], step: function(log) { this.depths.push(log.stack.peek(-1)); }, fault: function() {}, result: function() { return this.depths; }}")
+	tracer, err := New("{depths: [], step: function(log) { this.depths.push(log.stack.peek(-1)); }, fault: function() {}, result: function() { return this.depths; }}", true)
 	if err != nil {
 		t.Fatal(err)
 	}
@@ -93,7 +93,7 @@ func TestRegressionPanicPeek(t *testing.T) {
 
 // TestRegressionPanicSlice tests that we don't panic on bad arguments to memory getUint
 func TestRegressionPanicGetUint(t *testing.T) {
-	tracer, err := New("{ depths: [], step: function(log, db) { this.depths.push(log.memory.getUint(-64));}, fault: function() {}, result: function() { return this.depths; }}")
+	tracer, err := New("{ depths: [], step: function(log, db) { this.depths.push(log.memory.getUint(-64));}, fault: function() {}, result: function() { return this.depths; }}", true)
 	if err != nil {
 		t.Fatal(err)
 	}
@@ -104,7 +104,7 @@ func TestRegressionPanicGetUint(t *testing.T) {
 
 // TestTracingDeepObject tests if it returns an expected error when the json object has too many recursive children
 func TestTracingDeepObject(t *testing.T) {
-	tracer, err := New("{step: function() {}, fault: function() {}, result: function() { var o={}; var x=o; for (var i=0; i<1000; i++){ o.foo={}; o=o.foo; } return x; }}")
+	tracer, err := New("{step: function() {}, fault: function() {}, result: function() { var o={}; var x=o; for (var i=0; i<1000; i++){ o.foo={}; o=o.foo; } return x; }}", true)
 	if err != nil {
 		t.Fatal(err)
 	}
@@ -117,7 +117,7 @@ func TestTracingDeepObject(t *testing.T) {
 }
 
 func TestTracing(t *testing.T) {
-	tracer, err := New("{count: 0, step: function() { this.count += 1; }, fault: function() {}, result: function() { return this.count; }}")
+	tracer, err := New("{count: 0, step: function() { this.count += 1; }, fault: function() {}, result: function() { return this.count; }}", true)
 	if err != nil {
 		t.Fatal(err)
 	}
@@ -131,8 +131,15 @@ func TestTracing(t *testing.T) {
 	}
 }
 
+func TestUnsafeTracingDisabled(t *testing.T) {
+	_, err := New("{count: 0, step: function() { this.count += 1; }, fault: function() {}, result: function() { return this.count; }}", false)
+	if err == nil || err.Error() != "Only predefined tracers are supported" {
+		t.Fatal("Must disable JS code based tracers if unsafe")
+	}
+}
+
 func TestStack(t *testing.T) {
-	tracer, err := New("{depths: [], step: function(log) { this.depths.push(log.stack.length()); }, fault: function() {}, result: function() { return this.depths; }}")
+	tracer, err := New("{depths: [], step: function(log) { this.depths.push(log.stack.length()); }, fault: function() {}, result: function() { return this.depths; }}", true)
 	if err != nil {
 		t.Fatal(err)
 	}
@@ -147,7 +154,7 @@ func TestStack(t *testing.T) {
 }
 
 func TestOpcodes(t *testing.T) {
-	tracer, err := New("{opcodes: [], step: function(log) { this.opcodes.push(log.op.toString()); }, fault: function() {}, result: function() { return this.opcodes; }}")
+	tracer, err := New("{opcodes: [], step: function(log) { this.opcodes.push(log.op.toString()); }, fault: function() {}, result: function() { return this.opcodes; }}", true)
 	if err != nil {
 		t.Fatal(err)
 	}
@@ -165,7 +172,7 @@ func TestHalt(t *testing.T) {
 	t.Skip("duktape doesn't support abortion")
 
 	timeout := errors.New("stahp")
-	tracer, err := New("{step: function() { while(1); }, result: function() { return null; }}")
+	tracer, err := New("{step: function() { while(1); }, result: function() { return null; }}", true)
 	if err != nil {
 		t.Fatal(err)
 	}
@@ -181,7 +188,7 @@ func TestHalt(t *testing.T) {
 }
 
 func TestHaltBetweenSteps(t *testing.T) {
-	tracer, err := New("{step: function() {}, fault: function() {}, result: function() { return null; }}")
+	tracer, err := New("{step: function() {}, fault: function() {}, result: function() { return null; }}", true)
 	if err != nil {
 		t.Fatal(err)
 	}
```

### node/cn/tracers/tracers_test.go
```diff
@@ -133,7 +133,7 @@ func TestPrestateTracerCreate2(t *testing.T) {
 	}
 	statedb := tests.MakePreState(database.NewMemoryDBManager(), alloc)
 	// Create the tracer, the EVM environment and run it
-	tracer, err := New("prestateTracer")
+	tracer, err := New("prestateTracer", false)
 	if err != nil {
 		t.Fatalf("failed to create call tracer: %v", err)
 	}
@@ -300,7 +300,7 @@ func TestCallTracer(t *testing.T) {
 			statedb := tests.MakePreState(database.NewMemoryDBManager(), test.Genesis.Alloc)
 
 			// Create the tracer, the EVM environment and run it
-			tracer, err := New("callTracer")
+			tracer, err := New("callTracer", false)
 			if err != nil {
 				t.Fatalf("failed to create call tracer: %v", err)
 			}
```

### node/node.go
```diff
@@ -782,14 +782,13 @@ func (n *Node) apis() []rpc.API {
 			Service:   NewPublicAdminAPI(n),
 			Public:    true,
 		}, {
-			Namespace: "debug",
+			Namespace: "unsafedebug",
 			Version:   "1.0",
 			Service:   debug.Handler,
 		}, {
-			Namespace: "debug",
+			Namespace: "unsafedebug",
 			Version:   "1.0",
 			Service:   NewPublicDebugAPI(n),
-			Public:    true,
 		}, {
 			// "web3" namespace will be deprecated soon. The same APIs in "web3" are available in "klay" namespace.
 			Namespace: "web3",
```
