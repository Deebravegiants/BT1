# [?] Merge branch 'dev' of github.com:klaytn/klaytn into fix-nil-proposer-panic

## Summary
Severity: Unknown
Chain: Kaia
Component: kaiachain/kaia
Published: 2022-11-14
Source: https://github.com/kaiachain/kaia/commit/52e6b0271f4825d277ee0e6429a00b632b2859db
Type: security-commit

## Details
Merge branch 'dev' of github.com:klaytn/klaytn into fix-nil-proposer-panic

## Patch
### .dockerignore
```diff
@@ -1,8 +1,3 @@
-**/.git
-.git
-!.git/HEAD
-!.git/refs/heads
-
 build/_workspace
 build/_bin
 
```

### .github/workflows/CodeQL.yml
```diff
@@ -0,0 +1,51 @@
+name: "Code Scanning - Action"
+
+on:
+  pull_request:
+    branches: [dev, master]
+    types: [opened, synchronize]
+
+jobs:
+  CodeQL-Build:
+    # CodeQL runs on ubuntu-latest, windows-latest, and macos-latest
+    runs-on: ubuntu-latest
+
+    permissions:
+      # required for all workflows
+      security-events: write
+
+      # only required for workflows in private repositories
+      actions: read
+      contents: read
+
+    steps:
+      - name: Checkout repository
+        uses: actions/checkout@v3
+
+      # Initializes the CodeQL tools for scanning.
+      - name: Initialize CodeQL
+        uses: github/codeql-action/init@v2
+        with:
+          languages: go
+        # Override language selection by uncommenting this and choosing your languages
+        # with:
+        #   languages: go, javascript, csharp, python, cpp, java
+
+      # Autobuild attempts to build any compiled languages (C/C++, C#, or Java).
+      # If this step fails, then you should remove it and run the build manually (see below).
+      # - name: Autobuild
+      #   uses: github/codeql-action/autobuild@v2
+
+      # ℹ️ Command-line programs to run using the OS shell.
+      # 📚 See https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions#jobsjob_idstepsrun
+
+      # ✏️ If the Autobuild fails above, remove it and uncomment the following
+      #    three lines and modify them (or add more) to build your code if your
+      #    project uses a compiled language
+
+      #- run: |
+      #     make bootstrap
+      #     make release
+
+      - name: Perform CodeQL Analysis
+        uses: github/codeql-action/analyze@v2
```

### Dockerfile
```diff
@@ -17,18 +17,18 @@ ENV KLAYTN_STATIC_LINK=$KLAYTN_STATIC_LINK
 ARG KLAYTN_DISABLE_SYMBOL=0
 ENV KLAYTN_DISABLE_SYMBOL=$KLAYTN_DISABLE_SYMBOL
 
-RUN git init
-ADD . $SRC_DIR
-RUN git init
-RUN cd $SRC_DIR && make all
+WORKDIR $SRC_DIR
+ADD . .
+RUN make all
 
 FROM --platform=linux/amd64 ubuntu:20.04
 ARG SRC_DIR
 ARG PKG_DIR
 
-RUN apt update
-RUN apt install -yq musl-dev
-RUN mkdir -p $PKG_DIR/conf $PKG_DIR/bin
+RUN apt update && \
+            apt install -yq musl-dev ca-certificates && \
+            update-ca-certificates && \
+            mkdir -p $PKG_DIR/conf $PKG_DIR/bin
 
 # Startup scripts and binaries must be in the same location
 COPY --from=builder $SRC_DIR/build/bin/* $PKG_DIR/bin/
```

### README.md
```diff
@@ -4,6 +4,11 @@
 [![GoDoc](https://godoc.org/github.com/klaytn/klaytn?status.svg)](https://pkg.go.dev/github.com/klaytn/klaytn)
 [![Gitter](https://badges.gitter.im/klaytn/Lobby.svg)](https://gitter.im/klaytn/Lobby?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge)
 
+# Branch name will be changed
+
+We will change the `master` branch to `main` on Nov 1, 2022.
+After the branch policy change, please check your local or forked repository settings.
+
 # Klaytn
 
 Official golang implementation of the Klaytn protocol. Please visit [KlaytnDocs](https://docs.klaytn.com/) for more details on Klaytn design, node operation guides and application development resources.
```

### accounts/abi/bind/backends/simulated.go
```diff
@@ -677,6 +677,10 @@ type filterBackend struct {
 func (fb *filterBackend) ChainDB() database.DBManager { return fb.db }
 func (fb *filterBackend) EventMux() *event.TypeMux    { panic("not supported") }
 
+func (fb *filterBackend) HeaderByHash(ctx context.Context, hash common.Hash) (*types.Header, error) {
+	return fb.bc.GetHeaderByHash(hash), nil
+}
+
 func (fb *filterBackend) HeaderByNumber(_ context.Context, block rpc.BlockNumber) (*types.Header, error) {
 	if block == rpc.LatestBlockNumber {
 		return fb.bc.CurrentHeader(), nil
```

### blockchain/blockchain.go
```diff
@@ -130,6 +130,7 @@ type CacheConfig struct {
 	SenderTxHashIndexing bool                         // Enables saving senderTxHash to txHash mapping information to database and cache
 	TrieNodeCacheConfig  *statedb.TrieNodeCacheConfig // Configures trie node cache
 	SnapshotCacheSize    int                          // Memory allowance (MB) to use for caching snapshot entries in memory
+	SnapshotAsyncGen     bool                         // Enables snapshot data generation asynchronously
 }
 
 // gcBlock is used for priority queue for GC.
@@ -153,9 +154,8 @@ type gcBlock struct {
 // included in the canonical one where as GetBlockByNumber always represents the
 // canonical chain.
 type BlockChain struct {
-	chainConfig   *params.ChainConfig // Chain & network configuration
-	chainConfigMu *sync.RWMutex
-	cacheConfig   *CacheConfig // stateDB caching and trie caching/pruning configuration
+	chainConfig *params.ChainConfig // Chain & network configuration
+	cacheConfig *CacheConfig        // stateDB caching and trie caching/pruning configuration
 
 	db      database.DBManager // Low level persistent database to store final content in
 	snaps   *snapshot.Tree     // Snapshot tree for fast trie leaf access
@@ -230,6 +230,7 @@ func NewBlockChain(db database.DBManager, cacheConfig *CacheConfig, chainConfig
 			TriesInMemory:       DefaultTriesInMemory,
 			TrieNodeCacheConfig: statedb.GetEmptyTrieNodeCacheConfig(),
 			SnapshotCacheSize:   512,
+			SnapshotAsyncGen:    true,
 		}
 	}
 
@@ -246,7 +247,6 @@ func NewBlockChain(db database.DBManager, cacheConfig *CacheConfig, chainConfig
 
 	bc := &BlockChain{
 		chainConfig:        chainConfig,
-		chainConfigMu:      new(sync.RWMutex),
 		cacheConfig:        cacheConfig,
 		db:                 db,
 		triegc:             prque.New(),
@@ -344,7 +344,7 @@ func NewBlockChain(db database.DBManager, cacheConfig *CacheConfig, chainConfig
 			logger.Warn("Enabling snapshot recovery", "chainhead", head.NumberU64(), "diskbase", *layer)
 			recover = true
 		}
-		bc.snaps, _ = snapshot.New(bc.db, bc.stateCache.TrieDB(), bc.cacheConfig.SnapshotCacheSize, head.Root(), false, true, recover)
+		bc.snaps, _ = snapshot.New(bc.db, bc.stateCache.TrieDB(), bc.cacheConfig.SnapshotCacheSize, head.Root(), bc.cacheConfig.SnapshotAsyncGen, true, recover)
 	}
 
 	for i := 1; i <= bc.cacheConfig.TrieNodeCacheConfig.NumFetcherPrefetchWorker; i++ {
@@ -429,63 +429,13 @@ func (bc *BlockChain) SetCanonicalBlock(blockNum uint64) {
 }
 
 func (bc *BlockChain) UseGiniCoeff() bool {
-	bc.chainConfigMu.RLock()
-	defer bc.chainConfigMu.RUnlock()
-
 	return bc.chainConfig.Governance.Reward.UseGiniCoeff
 }
 
-func (bc *BlockChain) SetUseGiniCoeff(val bool) {
-	bc.chainConfigMu.Lock()
-	defer bc.chainConfigMu.Unlock()
-
-	bc.chainConfig.Governance.Reward.UseGiniCoeff = val
-}
-
 func (bc *BlockChain) ProposerPolicy() uint64 {
-	bc.chainConfigMu.RLock()
-	defer bc.chainConfigMu.RUnlock()
-
 	return bc.chainConfig.Istanbul.ProposerPolicy
 }
 
-func (bc *BlockChain) SetProposerPolicy(val uint64) {
-	bc.chainConfigMu.Lock()
-	defer bc.chainConfigMu.Unlock()
-
-	bc.chainConfig.Istanbul.ProposerPolicy = val
-}
-
-func (bc *BlockChain) SetLowerBoundBaseFee(val uint64) {
-	bc.chainConfigMu.Lock()
-	defer bc.chainConfigMu.Unlock()
-	bc.chainConfig.Governance.KIP71.LowerBoundBaseFee = val
-}
-
-func (bc *BlockChain) SetUpperBoundBaseFee(val uint64) {
-	bc.chainConfigMu.Lock()
-	defer bc.chainConfigMu.Unlock()
-	bc.chainConfig.Governance.KIP71.UpperBoundBaseFee = val
-}
-
-func (bc *BlockChain) SetGasTarget(val uint64) {
-	bc.chainConfigMu.Lock()
-	defer bc.chainConfigMu.Unlock()
-	bc.chainConfig.Governance.KIP71.GasTarget = val
-}
-
-func (bc *BlockChain) SetMaxBlockGasUsedForBaseFee(val uint64) {
-	bc.chainConfigMu.Lock()
-	defer bc.chainConfigMu.Unlock()
-	bc.chainConfig.Governance.KIP71.MaxBlockGasUsedForBaseFee = val
-}
-
-func (bc *BlockChain) SetBaseFeeDenominator(val uint64) {
-	bc.chainConfigMu.Lock()
-	defer bc.chainConfigMu.Unlock()
-	bc.chainConfig.Governance.KIP71.BaseFeeDenominator = val
-}
-
 func (bc *BlockChain) getProcInterrupt() bool {
 	return atomic.LoadInt32(&bc.procInterrupt) == 1
 }
```

### blockchain/chain_makers.go
```diff
@@ -178,6 +178,7 @@ func GenerateChain(config *params.ChainConfig, parent *types.Block, engine conse
 			TriesInMemory:       DefaultTriesInMemory,
 			TrieNodeCacheConfig: statedb.GetEmptyTrieNodeCacheConfig(),
 			SnapshotCacheSize:   512,
+			SnapshotAsyncGen:    true,
 		}
 		blockchain, _ := NewBlockChain(db, cacheConfig, config, engine, vm.Config{})
 		defer blockchain.Stop()
```

### blockchain/vm/evm.go
```diff
@@ -310,7 +310,7 @@ func (evm *EVM) CallCode(caller types.ContractRef, addr common.Address, input []
 	}
 
 	if !isProgramAccount(evm, caller.Address(), addr, evm.StateDB) {
-		logger.Info("Returning since the addr is not a program account", "addr", addr)
+		logger.Debug("Returning since the addr is not a program account", "addr", addr)
 		return nil, gas, nil
 	}
 
@@ -348,7 +348,7 @@ func (evm *EVM) DelegateCall(caller types.ContractRef, addr common.Address, inpu
 	}
 
 	if !isProgramAccount(evm, caller.Address(), addr, evm.StateDB) {
-		logger.Info("Returning since the addr is not a program account", "addr", addr)
+		logger.Debug("Returning since the addr is not a program account", "addr", addr)
 		return nil, gas, nil
 	}
 
@@ -392,7 +392,7 @@ func (evm *EVM) StaticCall(caller types.ContractRef, addr common.Address, input
 	}
 
 	if !isProgramAccount(evm, caller.Address(), addr, evm.StateDB) {
-		logger.Info("Returning since the addr is not a program account", "addr", addr)
+		logger.Debug("Returning since the addr is not a program account", "addr", addr)
 		return nil, gas, nil
 	}
 
```

### blockchain/vm/instructions.go
```diff
@@ -584,6 +584,13 @@ func opDifficulty(pc *uint64, evm *EVM, contract *Contract, memory *Memory, stac
 	return nil, nil
 }
 
+func opRandom(pc *uint64, evm *EVM, contract *Contract, memory *Memory, stack *Stack) ([]byte, error) {
+	// evm.BlockNumber.Uint64() is always greater or equal to 1
+	// since evm will not run on the genesis block
+	stack.push(evm.GetHash(evm.BlockNumber.Uint64() - 1).Big())
+	return nil, nil
+}
+
 func opGasLimit(pc *uint64, evm *EVM, contract *Contract, memory *Memory, stack *Stack) ([]byte, error) {
 	stack.push(math.U256(evm.interpreter.intPool.get().SetUint64(evm.GasLimit)))
 	return nil, nil
```

### blockchain/vm/instructions_test.go
```diff
@@ -839,6 +839,10 @@ func BenchmarkOpDifficulty(b *testing.B) {
 	opBenchmark(b, opDifficulty)
 }
 
+func BenchmarkOpRandom(b *testing.B) {
+	opBenchmark(b, opRandom)
+}
+
 func BenchmarkOpGasLimit(b *testing.B) {
 	opBenchmark(b, opGasLimit)
 }
```

### blockchain/vm/interpreter.go
```diff
@@ -89,6 +89,8 @@ func NewEVMInterpreter(evm *EVM, cfg *Config) *Interpreter {
 	if cfg.JumpTable[STOP] == nil {
 		var jt JumpTable
 		switch {
+		case evm.chainRules.IsKore:
+			jt = KoreInstructionSet
 		case evm.chainRules.IsLondon:
 			jt = LondonInstructionSet
 		case evm.chainRules.IsIstanbul:
```

### blockchain/vm/jump_table.go
```diff
@@ -64,11 +64,24 @@ var (
 	ConstantinopleInstructionSet = newConstantinopleInstructionSet()
 	IstanbulInstructionSet       = newIstanbulInstructionSet()
 	LondonInstructionSet         = newLondonInstructionSet()
+	KoreInstructionSet           = newKoreInstructionSet()
 )
 
 // JumpTable contains the EVM opcodes supported at a given fork.
 type JumpTable [256]*operation
 
+func newKoreInstructionSet() JumpTable {
+	instructionSet := newLondonInstructionSet()
+	instructionSet[PREVRANDAO] = &operation{
+		execute:         opRandom,
+		constantGas:     GasQuickStep,
+		minStack:        minStack(0, 1),
+		maxStack:        maxStack(0, 1),
+		computationCost: params.RandomComputationCost,
+	}
+	return instructionSet
+}
+
 // newLondonInstructionSet returns the frontier, homestead, byzantium,
 // constantinople, istanbul, petersburg, berlin and london instructions.
 func newLondonInstructionSet() JumpTable {
```
