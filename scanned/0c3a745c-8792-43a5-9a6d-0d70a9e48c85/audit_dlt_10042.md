# [?] Merge branch 'fixes-and-updates' of https://github.com/multiversx/mx-chain-go-ghsa-h96q-rcp8-pj69 into avoid-duplicated-hashes

## Summary
Severity: Unknown
Chain: MultiversX
Component: multiversx/mx-chain-go
Published: 2026-05-20
Source: https://github.com/multiversx/mx-chain-go/commit/c37db94aa9a41967745eddbc52865c7b50c5f558
Type: security-commit

## Details
Merge branch 'fixes-and-updates' of https://github.com/multiversx/mx-chain-go-ghsa-h96q-rcp8-pj69 into avoid-duplicated-hashes

## Patch
### cmd/node/config/config.toml
```diff
@@ -119,6 +119,7 @@
         BatchDelaySeconds = 2
         MaxBatchSize = 100
         MaxOpenFiles = 10
+        BloomFilterBitsPerKey = 10
 
 [ReceiptsStorage]
     [ReceiptsStorage.Cache]
@@ -132,6 +133,7 @@
         BatchDelaySeconds = 2
         MaxBatchSize = 100
         MaxOpenFiles = 10
+        BloomFilterBitsPerKey = 10
 
 [ScheduledSCRsStorage]
     [ScheduledSCRsStorage.Cache]
@@ -145,6 +147,7 @@
         BatchDelaySeconds = 2
         MaxBatchSize = 100
         MaxOpenFiles = 10
+        BloomFilterBitsPerKey = 10
 
 [PeerBlockBodyStorage]
     [PeerBlockBodyStorage.Cache]
@@ -158,6 +161,7 @@
         BatchDelaySeconds = 2
         MaxBatchSize = 100
         MaxOpenFiles = 10
+        BloomFilterBitsPerKey = 10
 
 [BlockHeaderStorage]
     [BlockHeaderStorage.Cache]
@@ -171,6 +175,7 @@
         BatchDelaySeconds = 2
         MaxBatchSize = 100
         MaxOpenFiles = 10
+        BloomFilterBitsPerKey = 10
 
 [BootstrapStorage]
     [BootstrapStorage.Cache]
@@ -184,6 +189,7 @@
         BatchDelaySeconds = 2
         MaxBatchSize = 100
         MaxOpenFiles = 10
+        BloomFilterBitsPerKey = 10
 
 [MetaBlockStorage]
     [MetaBlockStorage.Cache]
@@ -197,6 +203,7 @@
         BatchDelaySeconds = 2
         MaxBatchSize = 100
         MaxOpenFiles = 10
+        BloomFilterBitsPerKey = 10
 
 [ProofsStorage]
     [ProofsStorage.Cache]
@@ -210,6 +217,7 @@
         BatchDelaySeconds = 2
         MaxBatchSize = 100
         MaxOpenFiles = 10
+        BloomFilterBitsPerKey = 10
 
 [TxStorage]
     [TxStorage.Cache]
@@ -223,6 +231,7 @@
         BatchDelaySeconds = 2
         MaxBatchSize = 30000
         MaxOpenFiles = 10
+        BloomFilterBitsPerKey = 10
 
 [UnsignedTransactionStorage]
     [UnsignedTransactionStorage.Cache]
@@ -236,6 +245,7 @@
         BatchDelaySeconds = 2
         MaxBatchSize = 20000
         MaxOpenFiles = 10
+        BloomFilterBitsPerKey = 10
 
 [RewardTxStorage]
     [RewardTxStorage.Cache]
@@ -249,6 +259,7 @@
         BatchDelaySeconds = 2
         MaxBatchSize = 20000
         MaxOpenFiles = 10
+        BloomFilterBitsPerKey = 10
 
 [SmartContractsStorage]
     [SmartContractsStorage.Cache]
@@ -262,6 +273,7 @@
         BatchDelaySeconds = 2
         MaxBatchSize = 100
         MaxOpenFiles = 10
+        BloomFilterBitsPerKey = 10
 
 [SmartContractsStorageSimulate]
     [SmartContractsStorageSimulate.Cache]
@@ -275,6 +287,7 @@
         BatchDelaySeconds = 2
         MaxBatchSize = 100
         MaxOpenFiles = 10
+        BloomFilterBitsPerKey = 10
 
 [SmartContractsStorageForSCQuery]
     [SmartContractsStorageForSCQuery.Cache]
@@ -288,6 +301,7 @@
         BatchDelaySeconds = 2
         MaxBatchSize = 100
         MaxOpenFiles = 10
+        BloomFilterBitsPerKey = 10
 
 [StatusMetricsStorage]
     [StatusMetricsStorage.Cache]
@@ -300,6 +314,7 @@
         BatchDelaySeconds = 2
         MaxBatchSize = 100
         MaxOpenFiles = 10
+        BloomFilterBitsPerKey = 10
 
 [TrieEpochRootHashStorage]
     [TrieEpochRootHashStorage.Cache]
@@ -313,6 +328,7 @@
         BatchDelaySeconds = 2
         MaxBatchSize = 500
         MaxOpenFiles = 10
+        BloomFilterBitsPerKey = 10
 
 [ShardHdrNonceHashStorage]
     [ShardHdrNonceHashStorage.Cache]
@@ -326,6 +342,7 @@
         BatchDelaySeconds = 2
         MaxBatchSize = 100
         MaxOpenFiles = 10
+        BloomFilterBitsPerKey = 10
 
 [MetaHdrNonceHashStorage]
     [MetaHdrNonceHashStorage.Cache]
@@ -339,6 +356,7 @@
         BatchDelaySeconds = 2
         MaxBatchSize = 100
         MaxOpenFiles = 10
+        BloomFilterBitsPerKey = 10
 
 [AccountsTrieStorage]
     [AccountsTrieStorage.Cache]
@@ -367,6 +385,7 @@
         BatchDelaySeconds = 2
         MaxBatchSize = 100
         MaxOpenFiles = 10
+        BloomFilterBitsPerKey = 10
 
 [PeerAccountsTrieStorage]
     [PeerAccountsTrieStorage.Cache]
@@ -393,6 +412,7 @@
         BatchDelaySeconds = 2
         MaxBatchSize = 100
         MaxOpenFiles = 10
+        BloomFilterBitsPerKey = 10
 
 [TrieStorageManagerConfig]
     PruningBufferLen = 100000
@@ -530,11 +550,14 @@
         MaxBatchSize = 45000
         MaxOpenFiles = 10
         UseTmpAsFilePath = true
+        BloomFilterBitsPerKey = 10
 
 [Antiflood]
     Enabled = true
     NumConcurrentResolverJobs = 50
     NumConcurrentResolvingTrieNodesJobs = 3
+    MaxAllowedTrieNodeChunks = 10
+    TrieNodeChunksInactivityTimeoutInSec = 10
     [Antiflood.FastReacting]
         IntervalInSeconds = 1
         ReservedPercent   = 20.0
@@ -780,6 +803,7 @@
             BatchDelaySeconds = 2
             MaxBatchSize = 1000
             MaxOpenFiles = 10
+            BloomFilterBitsPerKey = 10
     [Hardfork.ExportKeysStorageConfig]
         [Hardfork.ExportKeysStorageConfig.Cache]
             Name = "HardFork.ExportKeysStorageConfig"
@@ -791,6 +815,7 @@
             BatchDelaySeconds = 2
             MaxBatchSize = 1000
             MaxOpenFiles = 10
+            BloomFilterBitsPerKey = 10
     [Hardfork.ExportTriesStorageConfig]
         [Hardfork.ExportTriesStorageConfig.Cache]
             Name = "HardFork.ExportTriesStorageConfig"
@@ -802,6 +827,7 @@
             BatchDelaySeconds = 2
             MaxBatchSize = 1000
             MaxOpenFiles = 10
+            BloomFilterBitsPerKey = 10
     [Hardfork.ImportStateStorageConfig]
         [Hardfork.ImportStateStorageConfig.Cache]
             Name = "HardFork.ImportStateStorageConfig"
@@ -813,6 +839,7 @@
             BatchDelaySeconds = 2
             MaxBatchSize = 1000
             MaxOpenFiles = 10
+            BloomFilterBitsPerKey = 10
     [Hardfork.ImportKeysStorageConfig]
         [Hardfork.ImportKeysStorageConfig.Cache]
             Name = "HardFork.ImportKeysStorageConfig"
@@ -824,6 +851,7 @@
             BatchDelaySeconds = 2
             MaxBatchSize = 1000
             MaxOpenFiles = 10
+            BloomFilterBitsPerKey = 10
 
 [Debug]
     [Debug.InterceptorResolver]
@@ -882,6 +910,7 @@
         BatchDelaySeconds = 2
         MaxBatchSize = 100
         MaxOpenFiles = 10
+        BloomFilterBitsPerKey = 10
 
 [DbLookupExtensions]
     Enabled = false
@@ -896,6 +925,7 @@
         BatchDelaySeconds = 2
         MaxBatchSize = 20000
         MaxOpenFiles = 10
+        BloomFilterBitsPerKey = 10
     [DbLookupExtensions.MiniblockHashByTxHashStorageConfig.Cache]
         Name = "DbLookupExtensions.MiniblockHashByTxHashStorage"
         Capacity = 20000
@@ -906,6 +936,7 @@
         BatchDelaySeconds = 2
         MaxBatchSize = 20000
         MaxOpenFiles = 10
+        BloomFilterBitsPerKey = 10
     [DbLookupExtensions.EpochByHashStorageConfig.Cache]
         Name = "DbLookupExtensions.EpochByHashStorage"
         Capacity = 20000
@@ -916,6 +947,7 @@
         BatchDelaySeconds = 2
         MaxBatchSize = 20000
         MaxOpenFiles = 10
+        BloomFilterBitsPerKey = 10
     [DbLookupExtensions.ResultsHashesByTxHashStorageConfig.Cache]
         Name = "DbLookupExtensions.ResultsHashesByTxHashStorage"
         Capacity = 20000
@@ -926,6 +958,7 @@
         BatchDelaySeconds = 2
         MaxBatchSize = 20000
         MaxOpenFiles = 10
+        BloomFilterBitsPerKey = 10
     [DbLookupExtensions.ESDTSuppliesStorageConfig.Cache]
         Name = "DbLookupExtensions.ESDTSuppliesStorage"
         Capacity = 20000
@@ -936,6 +969,7 @@
         BatchDelaySeconds = 2
         MaxBatchSize = 20000
         MaxOpenFiles = 10
+        BloomFilterBitsPerKey = 10
     [DbLookupExtensions.RoundHashStorageConfig.Cache]
         Name = "DbLookupExtensions.RoundHashStorage"
         Capacity = 20000
@@ -946,6 +980,7 @@
         BatchDelaySeconds = 2
         MaxBatchSize = 20000
         MaxOpenFiles = 10
+        BloomFilterBitsPerKey = 10
 
 [Logs]
     LogFileLifeSpanInMB = 1024 # 1GB
```

### common/common.go
```diff
@@ -9,8 +9,9 @@ import (
 
 	"github.com/multiversx/mx-chain-core-go/core"
 	"github.com/multiversx/mx-chain-core-go/data"
-	"github.com/multiversx/mx-chain-go/config"
 	logger "github.com/multiversx/mx-chain-logger-go"
+
+	"github.com/multiversx/mx-chain-go/config"
 )
 
 const (
@@ -105,6 +106,14 @@ func IsConsensusBitmapValid(
 		return ErrWrongSizeBitmap
 	}
 
+	paddingBits := consensusSize % 8
+	if paddingBits != 0 {
+		paddingMask := byte(0xFF << paddingBits)
+		if bitmap[len(bitmap)-1]&paddingMask != 0 {
+			return ErrPaddingBitsSet
+		}
+	}
+
 	numOfOnesInBitmap := 0
 	for index := range bitmap {
 		numOfOnesInBitmap += bits.OnesCount8(bitmap[index])
```

### common/common_test.go
```diff
@@ -9,12 +9,13 @@ import (
 	"github.com/multiversx/mx-chain-core-go/data/block"
 	"github.com/multiversx/mx-chain-core-go/data/smartContractResult"
 	"github.com/multiversx/mx-chain-core-go/data/transaction"
+	"github.com/stretchr/testify/require"
+
 	"github.com/multiversx/mx-chain-go/common"
 	"github.com/multiversx/mx-chain-go/config"
 	"github.com/multiversx/mx-chain-go/testscommon"
 	"github.com/multiversx/mx-chain-go/testscommon/chainParameters"
 	"github.com/multiversx/mx-chain-go/testscommon/enableEpochsHandlerMock"
-	"github.com/stretchr/testify/require"
 )
 
 var testFlag = core.EnableEpochFlag("test flag")
@@ -105,6 +106,29 @@ func TestIsConsensusBitmapValid(t *testing.T) {
 		require.Equal(t, common.ErrNotEnoughSignatures, err)
 	})
 
+	t.Run("padding bits set should return error", func(t *testing.T) {
+		t.Parallel()
+
+		// consensus size is 10, so bitmap should have 2 bytes
+		bitmap := make([]byte, len(pubKeys)/8+1)
+		bitmap[0] = 0xFF
+		bitmap[1] = 0x07
+
+		err := common.IsConsensusBitmapValid(log, pubKeys, bitmap, false)
+		require.Equal(t, common.ErrPaddingBitsSet, err)
+	})
+
+	t.Run("padding bits not set should return nil", func(t *testing.T) {
+		t.Parallel()
+
+		bitmap := make([]byte, len(pubKeys)/8+1)
+		bitmap[0] = 0xFF
+		bitmap[1] = 0x03
+
+		err := common.IsConsensusBitmapValid(log, pubKeys, bitmap, false)
+		require.Nil(t, err)
+	})
+
 	t.Run("should work", func(t *testing.T) {
 		t.Parallel()
 
```

### common/disabled/processStatusHandler.go
```diff
@@ -13,6 +13,9 @@ func NewProcessStatusHandler() *processStatusHandler {
 // SetBusy does nothing
 func (psh *processStatusHandler) SetBusy(_ string) {}
 
+// TrySetBusy returns true
+func (psh *processStatusHandler) TrySetBusy(_ string) bool { return true }
+
 // SetIdle does nothing
 func (psh *processStatusHandler) SetIdle() {}
 
```

### common/disabled/processStatusHandler_test.go
```diff
@@ -21,6 +21,7 @@ func TestProcessStatusHandler_MethodsShouldNotPanic(t *testing.T) {
 	psh := NewProcessStatusHandler()
 	assert.False(t, check.IfNil(psh))
 	psh.SetBusy("")
+	assert.True(t, psh.TrySetBusy(""))
 	psh.SetIdle()
 	assert.True(t, psh.IsIdle())
 }
```

### common/errors.go
```diff
@@ -34,3 +34,6 @@ var ErrInvalidHashShardKey = errors.New("invalid hash shard key")
 
 // ErrInvalidNonceShardKey signals that the provided nonce-shard key is invalid
 var ErrInvalidNonceShardKey = errors.New("invalid nonce shard key")
+
+// ErrPaddingBitsSet signals that the provided bitmap has padding bits set to 1 instead of 0
+var ErrPaddingBitsSet = errors.New("padding bits in the bitmap should be zero")
```

### common/interface.go
```diff
@@ -252,6 +252,7 @@ type StateStatisticsHandler interface {
 // able to tell if the node is idle or processing/committing a block
 type ProcessStatusHandler interface {
 	SetBusy(reason string)
+	TrySetBusy(reason string) bool
 	SetIdle()
 	IsIdle() bool
 	IsInterfaceNil() bool
```

### config/config.go
```diff
@@ -35,6 +35,9 @@ type DBConfig struct {
 	UseTmpAsFilePath    bool
 	ShardIDProviderType string
 	NumShards           int32
+	// BloomFilterBitsPerKey == 0, the Bloom filter is disabled.
+	// Otherwise, it specifies the number of bits per key used by the Bloom filter.
+	BloomFilterBitsPerKey int
 }
 
 // StorageConfig will map the storage unit configuration
@@ -395,16 +398,18 @@ type TxAccumulatorConfig struct {
 
 // AntifloodConfig will hold all p2p antiflood parameters
 type AntifloodConfig struct {
-	Enabled                             bool
-	NumConcurrentResolverJobs           int32
-	NumConcurrentResolvingTrieNodesJobs int32
-	OutOfSpecs                          FloodPreventerConfig
-	FastReacting                        FloodPreventerConfig
-	SlowReacting                        FloodPreventerConfig
-	PeerMaxOutput                       AntifloodLimitsConfig
-	Cache                               CacheConfig
-	Topic                               TopicAntifloodConfig
-	TxAccumulator                       TxAccumulatorConfig
+	Enabled                              bool
+	NumConcurrentResolverJobs            int32
+	NumConcurrentResolvingTrieNodesJobs  int32
+	MaxAllowedTrieNodeChunks             uint32
+	TrieNodeChunksInactivityTimeoutInSec int64
+	OutOfSpecs                           FloodPreventerConfig
+	FastReacting                         FloodPreventerConfig
+	SlowReacting                         FloodPreventerConfig
+	PeerMaxOutput                        AntifloodLimitsConfig
+	Cache                                CacheConfig
+	Topic                                TopicAntifloodConfig
+	TxAccumulator                        TxAccumulatorConfig
 }
 
 // FloodPreventerConfig will hold all flood preventer parameters
```

### consensus/broadcast/delayedBroadcast.go
```diff
@@ -16,6 +16,7 @@ import (
 	"github.com/multiversx/mx-chain-go/consensus"
 	"github.com/multiversx/mx-chain-go/consensus/broadcast/shared"
 	"github.com/multiversx/mx-chain-go/consensus/spos"
+	"github.com/multiversx/mx-chain-go/dataRetriever"
 	"github.com/multiversx/mx-chain-go/process"
 	"github.com/multiversx/mx-chain-go/process/factory"
 	"github.com/multiversx/mx-chain-go/sharding"
@@ -25,12 +26,16 @@ import (
 
 const prefixHeaderAlarm = "header_"
 const prefixDelayDataAlarm = "delay_"
-const sizeHeadersCache = 1000 // 1000 hashes in cache
+const sizeHeadersCache = 1000
+const sizeProcessedMetaHeadersCache = 100
+const maxPendingMetaHeaders = 50
 
 // ArgsDelayedBlockBroadcaster holds the arguments to create a delayed block broadcaster
 type ArgsDelayedBlockBroadcaster struct {
 	InterceptorsContainer process.InterceptorsContainer
 	HeadersSubscriber     consensus.HeadersPoolSubscriber
+	ProofsPool            dataRetriever.ProofsPool
+	EnableEpochsHandler   common.EnableEpochsHandler
 	ShardCoordinator      sharding.Coordinator
 	LeaderCacheSize       uint32
 	ValidatorCacheSize    uint32
@@ -50,11 +55,19 @@ type headerDataForValidator struct {
 	prevRandSeed []byte
 }
 
+type pendingHeaderInfo struct {
+	header data.HeaderHandler
+	hash   []byte
+	nonce  uint64
+}
+
 type delayedBlockBroadcaster struct {
 	alarm                      timersScheduler
 	interceptorsContainer      process.InterceptorsContainer
 	shardCoordinator           sharding.Coordinator
 	headersSubscriber          consensus.HeadersPoolSubscriber
+	proofsPool                 dataRetriever.ProofsPool
+	enableEpochsHandler        common.EnableEpochsHandler
 	valHeaderBroadcastData     []*shared.ValidatorHeaderBroadcastData
 	valBroadcastData           []*shared.DelayedBroadcastData
 	delayedBroadcastData       []*shared.DelayedBroadcastData
@@ -67,6 +80,11 @@ type delayedBlockBroadcaster struct {
 	broadcastConsensusMessage  func(message *consensus.Message) error
 	cacheHeaders               storage.Cacher
 	mutHeadersCache            sync.RWMutex
+	// pendingMetaHeaders stores metachain headers waiting for proof arrival before broadcast.
+	// mutPendingMetaHeaders and mutDataForBroadcast are never held simultaneously.
+	pendingMetaHeaders        map[string]*pendingHeaderInfo
+	mutPendingMetaHeaders     sync.RWMutex
+	cacheProcessedMetaHeaders storage.Cacher
 }
 
 // NewDelayedBlockBroadcaster create a new instance of a delayed block data broadcaster
@@ -83,17 +101,30 @@ func NewDelayedBlockBroadcaster(args *ArgsDelayedBlockBroadcaster) (*delayedBloc
 	if check.IfNil(args.AlarmScheduler) {
 		return nil, spos.ErrNilAlarmScheduler
 	}
+	if check.IfNil(args.ProofsPool) {
+		return nil, process.ErrNilProofsPool
+	}
+	if check.IfNil(args.EnableEpochsHandler) {
+		return nil, spos.ErrNilEnableEpochsHandler
+	}
 
 	cacheHeaders, err := cache.NewLRUCache(sizeHeadersCache)
 	if err != nil {
 		return nil, err
 	}
 
+	cacheProcessedMetaHeaders, err := cache.NewLRUCache(sizeProcessedMetaHeadersCache)
+	if err != nil {
+		return nil, err
+	}
+
 	dbb := &delayedBlockBroadcaster{
 		alarm:                      args.AlarmScheduler,
 		shardCoordinator:           args.ShardCoordinator,
 		interceptorsContainer:      args.InterceptorsContainer,
 		headersSubscriber:          args.HeadersSubscriber,
+		proofsPool:                 args.ProofsPool,
+		enableEpochsHandler:        args.EnableEpochsHandler,
 		valHeaderBroadcastData:     make([]*shared.ValidatorHeaderBroadcastData, 0),
 		valBroadcastData:           make([]*shared.DelayedBroadcastData, 0),
 		delayedBroadcastData:       make([]*shared.DelayedBroadcastData, 0),
@@ -102,9 +133,12 @@ func NewDelayedBlockBroadcaster(args *ArgsDelayedBlockBroadcaster) (*delayedBloc
 		mutDataForBroadcast:        sync.RWMutex{},
 		cacheHeaders:               cacheHeaders,
 		mutHeadersCache:            sync.RWMutex{},
+		pendingMetaHeaders:         make(map[string]*pendingHeaderInfo),
+		cacheProcessedMetaHeaders:  cacheProcessedMetaHeaders,
 	}
 
 	dbb.headersSubscriber.RegisterHandler(dbb.headerReceived)
+	dbb.proofsPool.RegisterHandler(dbb.proofReceived)
 	err = dbb.registerHeaderInterceptorCallback(dbb.interceptedHeader)
 	if err != nil {
 		return nil, err
@@ -261,42 +295,131 @@ func (dbb *delayedBlockBroadcaster) Close() {
 }
 
 func (dbb *delayedBlockBroadcaster) headerReceived(headerHandler data.HeaderHandler, headerHash []byte) {
+	if headerHandler.GetShardID() != core.MetachainShardId {
+		return
+	}
+
+	if !common.IsProofsFlagEnabledForHeader(dbb.enableEpochsHandler, headerHandler) {
+		dbb.processMetachainHeader(headerHandler, headerHash)
+		return
+	}
+
+	dbb.addPendingMetaHeader(headerHandler, headerHash)
+	dbb.tryProcessPendingMetaHeader(headerHash)
+}
+
+func (dbb *delayedBlockBroadcaster) proofReceived(proof data.HeaderProofHandler) {
+	if check.IfNil(proof) {
+		return
+	}
+	if proof.GetHeaderShardId() != core.MetachainShardId {
+		return
+	}
+
+	headerHash := proof.GetHeaderHash()
+	dbb.tryProcessPendingMetaHeader(headerHash)
+
+	dbb.mutPendingMetaHeaders.Lock()
+	dbb.evictPendingMetaHeadersUpToNonce(proof.GetHeaderNonce())
+	dbb.mutPendingMetaHeaders.Unlock()
+}
+
+func (dbb *delayedBlockBroadcaster) tryProcessPendingMetaHeader(headerHash []byte) {
+	dbb.mutPendingMetaHeaders.Lock()
+	hashStr := string(headerHash)
+	pending, found := dbb.pendingMetaHeaders[hashStr]
+	if !found {
+		dbb.mutPendingMetaHeaders.Unlock()
+		return
+	}
+	if !dbb.proofsPool.HasProof(core.MetachainShardId, headerHash) {
+		dbb.mutPendingMetaHeaders.Unlock()
+		return
+	}
+	delete(dbb.pendingMetaHeaders, hashStr)
+	dbb.mutPendingMetaHeaders.Unlock()
+
+	dbb.processMetachainHeader(pending.header, pending.hash)
+}
+
+func (dbb *delayedBlockBroadcaster) processMetachainHeader(headerHandler data.HeaderHandler, headerHash []byte) {
+	if alreadyProcessed, _ := dbb.cacheProcessedMetaHeaders.HasOrAdd(headerHash, struct{}{}, 0); alreadyProcessed {
+		return
+	}
+
 	dbb.mutDataForBroadcast.RLock()
 	defer dbb.mutDataForBroadcast.RUnlock()
 
 	if len(dbb.delayedBroadcastData) == 0 && len(dbb.valBroadcastData) == 0 {
 		return
 	}
-	if headerHandler.GetShardID() != core.MetachainShardId {
-		return
-	}
 
 	headerHashes, dataForValidators, err := getShardDataFromMetaChainBlock(
 		headerHandler,
 		dbb.shardCoordinator.SelfId(),
 	)
 	if err != nil {
-		log.Error("delayedBlockBroadcaster.headerReceived", "error", err.Error(),
+		log.Error("delayedBlockBroadcaster.processMetachainHeader", "error", err.Error(),
 			"headerHash", headerHash,
 		)
 		return
 	}
 	if len(headerHashes) == 0 {
-		log.Trace("delayedBlockBroadcaster.headerReceived: header received with no shardData for current shard",
+		log.Trace("delayedBlockBroadcaster.processMetachainHeader: no shardData for current shard",
 			"headerHash", headerHash,
 		)
 		return
 	}
 
-	log.Trace("delayedBlockBroadcaster.headerReceived", "nbHeaderHashes", len(headerHashes))
+	log.Trace("delayedBlockBroadcaster.processMetachainHeader", "nbHeaderHashes", len(headerHashes))
 	for i := range headerHashes {
-		log.Trace("delayedBlockBroadcaster.headerReceived", "headerHash", headerHashes[i])
+		log.Trace("delayedBlockBroadcaster.processMetachainHeader", "headerHash", headerHashes[i])
 	}
 
 	go dbb.scheduleValidatorBroadcast(dataForValidators)
 	go dbb.broadcastDataForHeaders(headerHashes)
 }
 
+func (dbb *delayedBlockBroadcaster) addPendingMetaHeader(header data.HeaderHandler, headerHash []byte) {
+	dbb.mutPendingMetaHeaders.Lock()
+	defer dbb.mutPendingMetaHeaders.Unlock()
+
+	if len(dbb.pendingMetaHeaders) >= maxPendingMetaHeaders {
+		dbb.evictOldestPendingMetaHeader()
+	}
+
+	dbb.pendingMetaHeaders[string(headerHash)] = &pendingHeaderInfo{
+		header: header,
+		hash:   headerHash,
+		nonce:  header.GetNonce(),
+	}
+}
+
+func (dbb *delayedBlockBroadcaster) evictOldestPendingMetaHeader() {
+	var oldestKey string
+	var oldestNonce uint64
+	first := true
+	for key, pending := range dbb.pendingMetaHeaders {
+		if first || pending.nonce < oldestNonce {
+			oldestKey = key
+			oldestNonce = pending.nonce
+			first = false
+		}
+	}
+	if !first {
+		delete(dbb.pendingMetaHeaders, oldestKey)
+	}
+}
+
+// must be called under mutPendingMetaHeaders lock
+func (dbb *delayedBlockBroadcaster) evictPendingMetaHeadersUpToNonce(nonce uint64) {
+	for key, pending := range dbb.pendingMetaHeaders {
+		if pending.nonce <= nonce {
+			delete(dbb.pendingMetaHeaders, key)
+		}
+	}
+}
+
 func (dbb *delayedBlockBroadcaster) broadcastDataForHeaders(headerHashes [][]byte) {
 	dbb.mutDataForBroadcast.RLock()
 	if len(dbb.delayedBroadcastData) == 0 {
```

### consensus/broadcast/delayedBroadcast_test.go
```diff
@@ -26,6 +26,8 @@ import (
 	"github.com/multiversx/mx-chain-go/consensus/spos"
 	"github.com/multiversx/mx-chain-go/process"
 	"github.com/multiversx/mx-chain-go/testscommon"
+	dataRetrieverMock "github.com/multiversx/mx-chain-go/testscommon/dataRetriever"
+	"github.com/multiversx/mx-chain-go/testscommon/enableEpochsHandlerMock"
 	"github.com/multiversx/mx-chain-go/testscommon/pool"
 )
 
@@ -137,6 +139,8 @@ func createDefaultDelayedBroadcasterArgs() *broadcast.ArgsDelayedBlockBroadcaste
 		ShardCoordinator:      &mock.ShardCoordinatorMock{},
 		InterceptorsContainer: interceptorsContainer,
 		HeadersSubscriber:     headersSubscriber,
+		ProofsPool:            &dataRetrieverMock.ProofsPoolMock{},
+		EnableEpochsHandler:   &enableEpochsHandlerMock.EnableEpochsHandlerStub{},
 		LeaderCacheSize:       2,
 		ValidatorCacheSize:    2,
 		AlarmScheduler:        alarm.NewAlarmScheduler(),
@@ -185,6 +189,26 @@ func TestNewDelayedBlockBroadcaster_NilAlarmSchedulerShouldErr(t *testing.T) {
 	require.Nil(t, dbb)
 }
 
+func TestNewDelayedBlockBroadcaster_NilProofsPoolShouldErr(t *testing.T) {
+	t.Parallel()
+
+	delayBroadcasterArgs := createDefaultDelayedBroadcasterArgs()
+	delayBroadcasterArgs.ProofsPool = nil
+	dbb, err := broadcast.NewDelayedBlockBroadcaster(delayBroadcasterArgs)
+	require.Equal(t, process.ErrNilProofsPool, err)
+	require.Nil(t, dbb)
+}
+
+func TestNewDelayedBlockBroadcaster_NilEnableEpochsHandlerShouldErr(t *testing.T) {
+	t.Parallel()
+
+	delayBroadcasterArgs := createDefaultDelayedBroadcasterArgs()
+	delayBroadcasterArgs.EnableEpochsHandler = nil
+	dbb, err := broadcast.NewDelayedBlockBroadcaster(delayBroadcasterArgs)
+	require.Equal(t, spos.ErrNilEnableEpochsHandler, err)
+	require.Nil(t, dbb)
+}
+
 func TestNewDelayedBlockBroadcasterOK(t *testing.T) {
 	t.Parallel()
 
@@ -387,7 +411,7 @@ func TestDelayedBlockBroadcaster_HeaderReceivedWithoutSignaturesForShardShouldNo
 	time.Sleep(sleepTime)
 
 	logOutputStr := observer.getBufferStr()
-	expectedLogMsg := "delayedBlockBroadcaster.headerReceived: header received with no shardData for current shard"
+	expectedLogMsg := "delayedBlockBroadcaster.processMetachainHeader: no shardData for current shard"
 	require.Contains(t, logOutputStr, expectedLogMsg)
 	require.Contains(t, logOutputStr, fmt.Sprintf("headerHash = %s", hex.EncodeToString(headerHash)))
 
@@ -1889,3 +1913,253 @@ func TestDelayedBlockBroadcaster_Close(t *testing.T) {
 	vbd = dbb.GetValidatorBroadcastData()
 	require.Equal(t, 1, len(vbd))
 }
+
+func TestDelayedBlockBroadcaster_HeaderReceivedWithProofsEnabled_DefersUntilProof(t *testing.T) {
+	t.Parallel()
+
+	mbBroadcastCalled := atomic.Flag{}
+	txBroadcastCalled := atomic.Flag{}
+
+	delayBroadcasterArgs := createDefaultDelayedBroadcasterArgs()
+	delayBroadcasterArgs.EnableEpochsHandler = &enableEpochsHandlerMock.EnableEpochsHandlerStub{
+		IsFlagEnabledInEpochCalled: func(flag core.EnableEpochFlag, epoch uint32) bool {
+			return flag == common.AndromedaFlag
+		},
+	}
+
+	hasProof := false
+	delayBroadcasterArgs.ProofsPool = &dataRetrieverMock.ProofsPoolMock{
+		HasProofCalled: func(shardID uint32, headerHash []byte) bool {
+			return hasProof
+		},
+	}
+
+	dbb, err := broadcast.NewDelayedBlockBroadcaster(delayBroadcasterArgs)
+	require.Nil(t, err)
+
+	err = dbb.SetBroadcastHandlers(
+		func(mbData map[uint32][]byte, pk []byte) error {
+			mbBroadcastCalled.SetValue(true)
+			return nil
+		},
+		func(txData map[string][][]byte, pk []byte) error {
+			txBroadcastCalled.SetValue(true)
+			return nil
+		},
+		func(header data.HeaderHandler, pk []byte) error { return nil },
+		func(message *consensus.Message) error { return nil },
+	)
+	require.Nil(t, err)
+
+	headerHash, _, miniblocksData, transactionsData := createDelayData("1")
+	delayedData := broadcast.CreateDelayBroadcastDataForLeader(headerHash, miniblocksData, transactionsData)
+	err = dbb.SetLeaderData(delayedData)
+	require.Nil(t, err)
+
+	metaBlock := createMetaBlock()
+	metaBlock.ShardInfo[0].HeaderHash = headerHash
+	metaBlock.Epoch = 1
+	metaBlock.Nonce = 10
+	metaHash := []byte("meta hash")
+
+	dbb.HeaderReceived(metaBlock, metaHash)
+
+	sleepTime := common.ExtraDelayForBroadcastBlockInfo +
+		common.ExtraDelayBetweenBroadcastMbsAndTxs +
+		100*time.Millisecond
+	time.Sleep(sleepTime)
+
+	assert.False(t, mbBroadcastCalled.IsSet(), "should not broadcast without proof")
+	assert.False(t, txBroadcastCalled.IsSet(), "should not broadcast without proof")
+	assert.Equal(t, 1, dbb.GetPendingMetaHeadersCount(), "header should be pending")
+
+	hasProof = true
+	proof := &block.HeaderProof{
+		HeaderHash:    metaHash,
+		HeaderShardId: core.MetachainShardId,
+		HeaderNonce:   10,
+		HeaderEpoch:   1,
+	}
+	dbb.ProofReceived(proof)
+
+	time.Sleep(sleepTime)
+
+	assert.True(t, mbBroadcastCalled.IsSet(), "should broadcast after proof arrives")
+	assert.True(t, txBroadcastCalled.IsSet(), "should broadcast after proof arrives")
+	assert.Equal(t, 0, dbb.GetPendingMetaHeadersCount(), "pending should be cleared")
+}
+
+func TestDelayedBlockBroadcaster_ProofReceivedEvictsOlderNonces(t *testing.T) {
+	t.Parallel()
+
+	delayBroadcasterArgs := createDefaultDelayedBroadcasterArgs()
+	delayBroadcasterArgs.EnableEpochsHandler = &enableEpochsHandlerMock.EnableEpochsHandlerStub{
+		IsFlagEnabledInEpochCalled: func(flag core.EnableEpochFlag, epoch uint32) bool {
+			return flag == common.AndromedaFlag
+		},
+	}
+	delayBroadcasterArgs.ProofsPool = &dataRetrieverMock.ProofsPoolMock{
+		HasProofCalled: func(shardID uint32, headerHash []byte) bool {
+			return false
+		},
+	}
+
+	dbb, err := broadcast.NewDelayedBlockBroadcaster(delayBroadcasterArgs)
+	require.Nil(t, err)
+
+	err = dbb.SetBroadcastHandlers(
+		func(mbData map[uint32][]byte, pk []byte) error { return nil },
+		func(txData map[string][][]byte, pk []byte) error { return nil },
+		func(header data.HeaderHandler, pk []byte) error { return nil },
+		func(message *consensus.Message) error { return nil },
+	)
+	require.Nil(t, err)
+
+	for i := 0; i < 3; i++ {
+		headerHash, _, miniblocksData, transactionsData := createDelayData(strconv.Itoa(i))
+		delayedData := broadcast.CreateDelayBroadcastDataForLeader(headerHash, miniblocksData, transactionsData)
+		err = dbb.SetLeaderData(delayedData)
+		require.Nil(t, err)
+
+		metaBlock := createMetaBlock()
+		metaBlock.ShardInfo[0].HeaderHash = headerHash
+		metaBlock.Epoch = 1
+		metaBlock.Nonce = uint64(10 + i)
+
+		dbb.HeaderReceived(metaBlock, []byte(fmt.Sprintf("meta hash %d", i)))
+	}
+
+	assert.Equal(t, 3, dbb.GetPendingMetaHeadersCount())
+
+	proof := &block.HeaderProof{
+		HeaderHash:    []byte("unknown hash"),
+		HeaderShardId: core.MetachainShardId,
+		HeaderNonce:   11,
+		HeaderEpoch:   1,
+	}
+	dbb.ProofReceived(proof)
+
+	assert.Equal(t, 1, dbb.GetPendingMetaHeadersCount(), "only nonce 12 should remain")
+}
+
+func TestDelayedBlockBroadcaster_HeaderReceivedWithProofsEnabled_ProofAlreadyAvailable(t *testing.T) {
+	t.Parallel()
+
+	mbBroadcastCalled := atomic.Flag{}
+
+	delayBroadcasterArgs := createDefaultDelayedBroadcasterArgs()
+	delayBroadcasterArgs.EnableEpochsHandler = &enableEpochsHandlerMock.EnableEpochsHandlerStub{
+		IsFlagEnabledInEpochCalled: func(flag core.EnableEpochFlag, epoch uint32) bool {
+			return flag == common.AndromedaFlag
+		},
+	}
+	delayBroadcasterArgs.ProofsPool = &dataRetrieverMock.ProofsPoolMock{
+		HasProofCalled: func(shardID uint32, headerHash []byte) bool {
+			return true
+		},
+	}
+
+	dbb, err := broadcast.NewDelayedBlockBroadcaster(delayBroadcasterArgs)
+	require.Nil(t, err)
+
+	err = dbb.SetBroadcastHandlers(
+		func(mbData map[uint32][]byte, pk []byte) error {
+			mbBroadcastCalled.SetValue(true)
+			return nil
+		},
+		func(txData map[string][][]byte, pk []byte) error { return nil },
+		func(header data.HeaderHandler, pk []byte) error { return nil },
+		func(message *consensus.Message) error { return nil },
+	)
+	require.Nil(t, err)
+
+	headerHash, _, miniblocksData, transactionsData := createDelayData("1")
+	delayedData := broadcast.CreateDelayBroadcastDataForLeader(headerHash, miniblocksData, transactionsData)
+	err = dbb.SetLeaderData(delayedData)
+	require.Nil(t, err)
+
+	metaBlock := createMetaBlock()
+	metaBlock.ShardInfo[0].HeaderHash = headerHash
+	metaBlock.Epoch = 1
+	metaBlock.Nonce = 10
+
+	dbb.HeaderReceived(metaBlock, []byte("meta hash"))
+
+	sleepTime := common.ExtraDelayForBroadcastBlockInfo +
+		common.ExtraDelayBetweenBroadcastMbsAndTxs +
+		100*time.Millisecond
+	time.Sleep(sleepTime)
+
+	assert.True(t, mbBroadcastCalled.IsSet(), "should broadcast immediately when proof is already available")
+	assert.Equal(t, 0, dbb.GetPendingMetaHeadersCount())
+}
+
+func TestDelayedBlockBroadcaster_DuplicateProcessingPrevented(t *testing.T) {
+	t.Parallel()
+
+	broadcastCount := atomic.Counter{}
+
+	delayBroadcasterArgs := createDefaultDelayedBroadcasterArgs()
+	delayBroadcasterArgs.EnableEpochsHandler = &enableEpochsHandlerMock.EnableEpochsHandlerStub{
+		IsFlagEnabledInEpochCalled: func(flag core.EnableEpochFlag, epoch uint32) bool {
+			return flag == common.AndromedaFlag
+		},
+	}
+	delayBroadcasterArgs.ProofsPool = &dataRetrieverMock.ProofsPoolMock{
+		HasProofCalled: func(shardID uint32, headerHash []byte) bool {
+			return true
+		},
+	}
+
+	dbb, err := broadcast.NewDelayedBlockBroadcaster(delayBroadcasterArgs)
+	require.Nil(t, err)
+
+	err = dbb.SetBroadcastHandlers(
+		func(mbData map[uint32][]byte, pk []byte) error {
+			broadcastCount.Increment()
+			return nil
+		},
+		func(txData map[string][][]byte, pk []byte) error { return nil },
+		func(header data.HeaderHandler, pk []byte) error { return nil },
+		func(message *consensus.Message) error { return nil },
+	)
+	require.Nil(t, err)
+
+	headerHash, _, miniblocksData, transactionsData := createDelayData("1")
+	delayedData := broadcast.CreateDelayBroadcastDataForLeader(headerHash, miniblocksData, transactionsData)
+	err = dbb.SetLeaderData(delayedData)
+	require.Nil(t, err)
+
+	metaBlock := createMetaBlock()
+	metaBlock.ShardInfo[0].HeaderHash = headerHash
+	metaBlock.Epoch = 1
+	metaBlock.Nonce = 10
+	metaHash := []byte("meta hash")
+
+	dbb.HeaderReceived(metaBlock, metaHash)
+	dbb.HeaderReceived(metaBlock, metaHash)
+
+	sleepTime := common.ExtraDelayForBroadcastBlockInfo +
+		common.ExtraDelayBetweenBroadcastMbsAndTxs +
+		100*time.Millisecond
+	time.Sleep(sleepTime)
+
+	assert.Equal(t, int64(1), broadcastCount.Get(), "should broadcast only once despite two HeaderReceived calls")
+}
+
+func TestDelayedBlockBroadcaster_ProofReceivedNonMetaShouldBeIgnored(t *testing.T) {
+	t.Parallel()
+
+	delayBroadcasterArgs := createDefaultDelayedBroadcasterArgs()
+	dbb, err := broadcast.NewDelayedBlockBroadcaster(delayBroadcasterArgs)
+	require.Nil(t, err)
+
+	proof := &block.HeaderProof{
+		HeaderHash:    []byte("some hash"),
+		HeaderShardId: 0,
+		HeaderNonce:   10,
+	}
+	dbb.ProofReceived(proof)
+
+	assert.Equal(t, 0, dbb.GetPendingMetaHeadersCount())
+}
```

### consensus/broadcast/export.go
```diff
@@ -81,6 +81,18 @@ func (dbb *delayedBlockBroadcaster) HeaderReceived(headerHandler data.HeaderHand
 	dbb.headerReceived(headerHandler, hash)
 }
 
+// ProofReceived is the callback for when a proof is received
+func (dbb *delayedBlockBroadcaster) ProofReceived(proof data.HeaderProofHandler) {
+	dbb.proofReceived(proof)
+}
+
+// GetPendingMetaHeadersCount returns the number of pending meta headers
+func (dbb *delayedBlockBroadcaster) GetPendingMetaHeadersCount() int {
+	dbb.mutPendingMetaHeaders.RLock()
+	defer dbb.mutPendingMetaHeaders.RUnlock()
+	return len(dbb.pendingMetaHeaders)
+}
+
 // GetValidatorBroadcastData returns the set validator delayed broadcast data
 func (dbb *delayedBlockBroadcaster) GetValidatorBroadcastData() []*shared.DelayedBroadcastData {
 	dbb.mutDataForBroadcast.RLock()
```

### consensus/broadcast/shardChainMessenger_test.go
```diff
@@ -26,6 +26,8 @@ import (
 	"github.com/multiversx/mx-chain-go/process"
 	"github.com/multiversx/mx-chain-go/process/factory"
 	"github.com/multiversx/mx-chain-go/testscommon"
+	dataRetrieverMock "github.com/multiversx/mx-chain-go/testscommon/dataRetriever"
+	"github.com/multiversx/mx-chain-go/testscommon/enableEpochsHandlerMock"
 	"github.com/multiversx/mx-chain-go/testscommon/hashingMocks"
 	"github.com/multiversx/mx-chain-go/testscommon/p2pmocks"
 )
@@ -572,6 +574,8 @@ func TestShardChainMessenger_BroadcastBlockDataLeaderShouldTriggerWaitingDelayed
 	argsDelayedBroadcaster := broadcast.ArgsDelayedBlockBroadcaster{
 		InterceptorsContainer: args.InterceptorsContainer,
 		HeadersSubscriber:     args.HeadersSubscriber,
+		ProofsPool:            &dataRetrieverMock.ProofsPoolMock{},
+		EnableEpochsHandler:   &enableEpochsHandlerMock.EnableEpochsHandlerStub{},
 		ShardCoordinator:      args.ShardCoordinator,
 		LeaderCacheSize:       args.MaxDelayCacheSize,
 		ValidatorCacheSize:    args.MaxDelayCacheSize,
```
