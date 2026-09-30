# [?] Merge branch 'advisory-fix' of https://github.com/multiversx/mx-chain-go-ghsa-pm7x-xvmm-jpfw into advisory-fix-1

## Summary
Severity: Unknown
Chain: MultiversX
Component: multiversx/mx-chain-go
Published: 2026-04-20
Source: https://github.com/multiversx/mx-chain-go/commit/3cd2268a59eeca264fe260e5108956985911eb07
Type: security-commit

## Details
Merge branch 'advisory-fix' of https://github.com/multiversx/mx-chain-go-ghsa-pm7x-xvmm-jpfw into advisory-fix-1

## Patch
### cmd/node/config/config.toml
```diff
@@ -963,6 +963,7 @@
     NumCrossShardPeers  = 2
     NumTotalPeers       = 3 # NumCrossShardPeers + num intra shard
     NumFullHistoryPeers = 3
+    RequestProofByNonceDelayMs = 100 # delay proof requests by nonce to allow the header to be received first
 
 [HeartbeatV2]
     PeerAuthenticationTimeBetweenSendsInSec          = 600   # 10min TODO: change this for mainnet/devnet/testnet
```

### config/config.go
```diff
@@ -169,14 +169,14 @@ type Config struct {
 	MetaBlockStorage StorageConfig
 	ProofsStorage    StorageConfig
 
-	AccountsTrieStorage      StorageConfig
-	PeerAccountsTrieStorage  StorageConfig
-	EvictionWaitingList      EvictionWaitingListConfig
-	StateTriesConfig         StateTriesConfig
+	AccountsTrieStorage          StorageConfig
+	PeerAccountsTrieStorage      StorageConfig
+	EvictionWaitingList          EvictionWaitingListConfig
+	StateTriesConfig             StateTriesConfig
 	StateAccessesCollectorConfig StateAccessesCollectorConfig
-	TrieStorageManagerConfig TrieStorageManagerConfig
-	TrieLeavesRetrieverConfig TrieLeavesRetrieverConfig
-	BadBlocksCache           CacheConfig
+	TrieStorageManagerConfig     TrieStorageManagerConfig
+	TrieLeavesRetrieverConfig    TrieLeavesRetrieverConfig
+	BadBlocksCache               CacheConfig
 
 	TxBlockBodyDataPool         CacheConfig
 	PeerBlockBodyDataPool       CacheConfig
@@ -667,9 +667,10 @@ type TrieSyncConfig struct {
 
 // RequesterConfig represents the config options to be used when setting up the requester instances
 type RequesterConfig struct {
-	NumCrossShardPeers  uint32
-	NumTotalPeers       uint32
-	NumFullHistoryPeers uint32
+	NumCrossShardPeers         uint32
+	NumTotalPeers              uint32
+	NumFullHistoryPeers        uint32
+	RequestProofByNonceDelayMs uint32
 }
 
 // PoolsCleanersConfig represents the config options to be used by the pools cleaners
```

### consensus/spos/worker.go
```diff
@@ -596,6 +596,10 @@ func (wrk *Worker) doJobOnMessageWithHeader(cnsMsg *consensus.Message) error {
 		return fmt.Errorf("%w : received header from consensus topic is invalid",
 			err)
 	}
+	if wrk.enableEpochsHandler.IsFlagEnabledInEpoch(common.AndromedaFlag, header.GetEpoch()) {
+		return fmt.Errorf("%w : received header on consensus topic after andromeda",
+			ErrInvalidHeader)
+	}
 
 	var valStatsRootHash []byte
 	metaHeader, ok := header.(data.MetaHeaderHandler)
```

### dataRetriever/requestHandlers/requestHandler.go
```diff
@@ -37,16 +37,17 @@ const uniqueEquivalentProofSuffix = "eqp"
 // TODO move the keys definitions that are whitelisted in core and use them in InterceptedData implementations, Identifiers() function
 
 type resolverRequestHandler struct {
-	mutEpoch              sync.RWMutex
-	epoch                 uint32
-	shardID               uint32
-	maxTxsToRequest       int
-	requestersFinder      dataRetriever.RequestersFinder
-	requestedItemsHandler dataRetriever.RequestedItemsHandler
-	whiteList             dataRetriever.WhiteListHandler
-	sweepTime             time.Time
-	requestInterval       time.Duration
-	mutSweepTime          sync.Mutex
+	mutEpoch                 sync.RWMutex
+	epoch                    uint32
+	shardID                  uint32
+	maxTxsToRequest          int
+	requestersFinder         dataRetriever.RequestersFinder
+	requestedItemsHandler    dataRetriever.RequestedItemsHandler
+	whiteList                dataRetriever.WhiteListHandler
+	sweepTime                time.Time
+	requestInterval          time.Duration
+	requestProofByNonceDelay time.Duration
+	mutSweepTime             sync.Mutex
 
 	trieHashesAccumulator map[string]struct{}
 	lastTrieRequestTime   time.Time
@@ -61,6 +62,7 @@ func NewResolverRequestHandler(
 	maxTxsToRequest int,
 	shardID uint32,
 	requestInterval time.Duration,
+	requestProofByNonceDelay time.Duration,
 ) (*resolverRequestHandler, error) {
 
 	if check.IfNil(finder) {
@@ -80,14 +82,15 @@ func NewResolverRequestHandler(
 	}
 
 	rrh := &resolverRequestHandler{
-		requestersFinder:      finder,
-		requestedItemsHandler: requestedItemsHandler,
-		epoch:                 uint32(0), // will be updated after creation of the request handler
-		shardID:               shardID,
-		maxTxsToRequest:       maxTxsToRequest,
-		whiteList:             whiteList,
-		requestInterval:       requestInterval,
-		trieHashesAccumulator: make(map[string]struct{}),
+		requestersFinder:         finder,
+		requestedItemsHandler:    requestedItemsHandler,
+		epoch:                    uint32(0), // will be updated after creation of the request handler
+		shardID:                  shardID,
+		maxTxsToRequest:          maxTxsToRequest,
+		whiteList:                whiteList,
+		requestInterval:          requestInterval,
+		requestProofByNonceDelay: requestProofByNonceDelay,
+		trieHashesAccumulator:    make(map[string]struct{}),
 	}
 
 	rrh.sweepTime = time.Now()
@@ -914,47 +917,56 @@ func (rrh *resolverRequestHandler) RequestEquivalentProofByHash(headerShard uint
 
 // RequestEquivalentProofByNonce asks for equivalent proof for the provided header nonce
 func (rrh *resolverRequestHandler) RequestEquivalentProofByNonce(headerShard uint32, headerNonce uint64) {
-	key := common.GetEquivalentProofNonceShardKey(headerNonce, headerShard)
-	if !rrh.testIfRequestIsNeeded([]byte(key), uniqueEquivalentProofSuffix) {
-		return
-	}
-
 	epoch := rrh.getEpoch()
-	log.Debug("requesting equivalent proof by nonce from network",
-		"headerNonce", headerNonce,
-		"headerShard", headerShard,
-		"epoch", epoch,
-	)
-
-	requester, err := rrh.getEquivalentProofsRequester(headerShard)
-	if err != nil {
-		log.Error("RequestEquivalentProofByNonce.getEquivalentProofsRequester",
-			"error", err.Error(),
-			"headerNonce", headerNonce,
-		)
-		return
-	}
+	rrh.RequestEquivalentProofByNonceForEpoch(headerShard, headerNonce, epoch)
+}
 
-	proofsRequester, ok := requester.(EquivalentProofsRequester)
-	if !ok {
-		log.Warn("wrong assertion type when creating equivalent proofs requester")
-		return
-	}
+// RequestEquivalentProofByNonceForEpoch asks for equivalent proof for the provided header nonce and epoch
+func (rrh *resolverRequestHandler) RequestEquivalentProofByNonceForEpoch(headerShard uint32, headerNonce uint64, epoch uint32) {
+	go func(requestEpoch uint32) {
+		key := common.GetEquivalentProofNonceShardKey(headerNonce, headerShard)
+		if !rrh.testIfRequestIsNeeded([]byte(key), uniqueEquivalentProofSuffix) {
+			return
+		}
 
-	rrh.whiteList.Add([][]byte{[]byte(key)})
+		time.Sleep(rrh.requestProofByNonceDelay)
 
-	err = proofsRequester.RequestDataFromNonce([]byte(key), epoch)
-	if err != nil {
-		log.Debug("RequestEquivalentProofByNonce.RequestDataFromNonce",
-			"error", err.Error(),
+		log.Debug("requesting equivalent proof by nonce from network",
 			"headerNonce", headerNonce,
 			"headerShard", headerShard,
 			"epoch", epoch,
 		)
-		return
-	}
 
-	rrh.addRequestedItems([][]byte{[]byte(key)}, uniqueEquivalentProofSuffix)
+		requester, err := rrh.getEquivalentProofsRequester(headerShard)
+		if err != nil {
+			log.Error("RequestEquivalentProofByNonceForEpoch.getEquivalentProofsRequester",
+				"error", err.Error(),
+				"headerNonce", headerNonce,
+			)
+			return
+		}
+
+		proofsRequester, ok := requester.(EquivalentProofsRequester)
+		if !ok {
+			log.Warn("wrong assertion type when creating equivalent proofs requester")
+			return
+		}
+
+		rrh.whiteList.Add([][]byte{[]byte(key)})
+
+		err = proofsRequester.RequestDataFromNonce([]byte(key), epoch)
+		if err != nil {
+			log.Debug("RequestEquivalentProofByNonceForEpoch.RequestDataFromNonce",
+				"error", err.Error(),
+				"headerNonce", headerNonce,
+				"headerShard", headerShard,
+				"epoch", epoch,
+			)
+			return
+		}
+
+		rrh.addRequestedItems([][]byte{[]byte(key)}, uniqueEquivalentProofSuffix)
+	}(epoch)
 }
 
 func (rrh *resolverRequestHandler) getEquivalentProofsRequester(headerShard uint32) (dataRetriever.Requester, error) {
```

### dataRetriever/requestHandlers/requestHandler_test.go
```diff
@@ -9,6 +9,7 @@ import (
 	"time"
 
 	"github.com/multiversx/mx-chain-core-go/core"
+
 	"github.com/multiversx/mx-chain-go/common"
 	"github.com/multiversx/mx-chain-go/dataRetriever"
 	"github.com/multiversx/mx-chain-go/dataRetriever/mock"
@@ -52,6 +53,7 @@ func TestNewResolverRequestHandler(t *testing.T) {
 			1,
 			0,
 			time.Second,
+			time.Millisecond,
 		)
 
 		assert.Nil(t, rrh)
@@ -67,6 +69,7 @@ func TestNewResolverRequestHandler(t *testing.T) {
 			1,
 			0,
 			time.Second,
+			time.Millisecond,
 		)
 
 		assert.Nil(t, rrh)
@@ -82,6 +85,7 @@ func TestNewResolverRequestHandler(t *testing.T) {
 			1,
 			0,
 			time.Second,
+			time.Millisecond,
 		)
 
 		assert.Nil(t, rrh)
@@ -97,6 +101,7 @@ func TestNewResolverRequestHandler(t *testing.T) {
 			0,
 			0,
 			time.Second,
+			time.Millisecond,
 		)
 
 		assert.Nil(t, rrh)
@@ -112,6 +117,7 @@ func TestNewResolverRequestHandler(t *testing.T) {
 			1,
 			0,
 			time.Millisecond-time.Nanosecond,
+			time.Millisecond,
 		)
 
 		assert.Nil(t, rrh)
@@ -127,6 +133,7 @@ func TestNewResolverRequestHandler(t *testing.T) {
 			1,
 			0,
 			time.Second,
+			time.Millisecond,
 		)
 
 		assert.Nil(t, err)
@@ -159,6 +166,7 @@ func TestResolverRequestHandler_RequestTransaction(t *testing.T) {
 			1,
 			0,
 			time.Second,
+			time.Millisecond,
 		)
 
 		rrh.RequestTransaction(0, make([][]byte, 0))
@@ -184,6 +192,7 @@ func TestResolverRequestHandler_RequestTransaction(t *testing.T) {
 			1,
 			0,
 			time.Second,
+			time.Millisecond,
 		)
 
 		rrh.RequestTransaction(0, [][]byte{[]byte("txHash")})
@@ -211,6 +220,7 @@ func TestResolverRequestHandler_RequestTransaction(t *testing.T) {
 			1,
 			0,
 			time.Second,
+			time.Millisecond,
 		)
 
 		rrh.RequestTransaction(0, [][]byte{[]byte("txHash")})
@@ -237,6 +247,7 @@ func TestResolverRequestHandler_RequestTransaction(t *testing.T) {
 			1,
 			0,
 			time.Second,
+			time.Millisecond,
 		)
 
 		rrh.RequestTransaction(0, [][]byte{[]byte("txHash")})
@@ -273,6 +284,7 @@ func TestResolverRequestHandler_RequestTransaction(t *testing.T) {
 			1,
 			0,
 			time.Second,
+			time.Millisecond,
 		)
 
 		rrh.RequestTransaction(0, [][]byte{[]byte("txHash")})
@@ -321,6 +333,7 @@ func TestResolverRequestHandler_RequestTransaction(t *testing.T) {
 			1,
 			0,
 			time.Second,
+			time.Millisecond,
 		)
 
 		rrh.RequestTransaction(0, [][]byte{[]byte("txHash")})
@@ -364,6 +377,7 @@ func TestResolverRequestHandler_RequestMiniBlock(t *testing.T) {
 			1,
 			0,
 			time.Second,
+			time.Millisecond,
 		)
 
 		rrh.RequestMiniBlock(0, make([]byte, 0))
@@ -389,6 +403,7 @@ func TestResolverRequestHandler_RequestMiniBlock(t *testing.T) {
 			1,
 			0,
 			time.Second,
+			time.Millisecond,
 		)
 
 		rrh.RequestMiniBlock(0, make([]byte, 0))
@@ -420,6 +435,7 @@ func TestResolverRequestHandler_RequestMiniBlock(t *testing.T) {
 			1,
 			0,
 			time.Second,
+			time.Millisecond,
 		)
 
 		rrh.RequestMiniBlock(0, []byte("mbHash"))
@@ -446,6 +462,7 @@ func TestResolverRequestHandler_RequestMiniBlock(t *testing.T) {
 			1,
 			0,
 			time.Second,
+			time.Millisecond,
 		)
 
 		rrh.RequestMiniBlock(0, []byte("mbHash"))
@@ -474,6 +491,7 @@ func TestResolverRequestHandler_RequestMiniBlock(t *testing.T) {
 			1,
 			0,
 			time.Second,
+			time.Millisecond,
 		)
 
 		rrh.SetEpoch(expectedEpoch)
@@ -499,6 +517,7 @@ func TestResolverRequestHandler_RequestShardHeader(t *testing.T) {
 			1,
 			0,
 			time.Second,
+			time.Millisecond,
 		)
 
 		rrh.RequestShardHeader(0, make([]byte, 0))
@@ -513,6 +532,7 @@ func TestResolverRequestHandler_RequestShardHeader(t *testing.T) {
 			1,
 			0,
 			time.Second,
+			time.Millisecond,
 		)
 
 		rrh.RequestShardHeader(1, make([]byte, 0))
@@ -537,6 +557,7 @@ func TestResolverRequestHandler_RequestShardHeader(t *testing.T) {
 			1,
 			0,
 			time.Second,
+			time.Millisecond,
 		)
 
 		rrh.RequestShardHeader(0, []byte("hdrHash"))
@@ -563,6 +584,7 @@ func TestResolverRequestHandler_RequestShardHeader(t *testing.T) {
 			1,
 			0,
 			time.Second,
+			time.Millisecond,
 		)
 
 		rrh.RequestShardHeader(0, []byte("hdrHash"))
@@ -588,6 +610,7 @@ func TestResolverRequestHandler_RequestMetaHeader(t *testing.T) {
 			1,
 			0,
 			time.Second,
+			time.Millisecond,
 		)
 
 		rrh.RequestMetaHeader([]byte("hdrHash"))
@@ -613,6 +636,7 @@ func TestResolverRequestHandler_RequestMetaHeader(t *testing.T) {
 			1,
 			0,
 			time.Second,
+			time.Millisecond,
 		)
 
 		rrh.RequestMetaHeader([]byte("hdrHash"))
@@ -631,6 +655,7 @@ func TestResolverRequestHandler_RequestMetaHeader(t *testing.T) {
 			1,
 			0,
 			time.Second,
+			time.Millisecond,
 		)
 
 		rrh.RequestMetaHeader([]byte("hdrHash"))
@@ -655,6 +680,7 @@ func TestResolverRequestHandler_RequestMetaHeader(t *testing.T) {
 			1,
 			0,
 			time.Second,
+			time.Millisecond,
 		)
 
 		rrh.RequestMetaHeader([]byte("hdrHash"))
@@ -681,6 +707,7 @@ func TestResolverRequestHandler_RequestMetaHeader(t *testing.T) {
 			1,
 			0,
 			time.Second,
+			time.Millisecond,
 		)
 
 		rrh.RequestMetaHeader([]byte("hdrHash"))
@@ -708,6 +735,7 @@ func TestResolverRequestHandler_RequestShardHeaderByNonce(t *testing.T) {
 			1,
 			0,
 			time.Second,
+			time.Millisecond,
 		)
 
 		rrh.RequestShardHeaderByNonce(0, 0)
@@ -729,6 +757,7 @@ func TestResolverRequestHandler_RequestShardHeaderByNonce(t *testing.T) {
 			1,
 			core.MetachainShardId,
 			time.Second,
+			time.Millisecond,
 		)
 
 		rrh.RequestShardHeaderByNonce(1, 0)
@@ -755,6 +784,7 @@ func TestResolverRequestHandler_RequestShardHeaderByNonce(t *testing.T) {
 			1,
 			0,
 			time.Second,
+			time.Millisecond,
 		)
 
 		rrh.RequestShardHeaderByNonce(0, 0)
@@ -782,6 +812,7 @@ func TestResolverRequestHandler_RequestShardHeaderByNonce(t *testing.T) {
 			1,
 			0,
 			time.Second,
+			time.Millisecond,
 		)
 
 		rrh.RequestShardHeaderByNonce(0, 0)
@@ -813,6 +844,7 @@ func TestResolverRequestHandler_RequestShardHeaderByNonce(t *testing.T) {
 			1,
 			0,
 			time.Second,
+			time.Millisecond,
 		)
 
 		rrh.RequestShardHeaderByNonce(0, 0)
@@ -839,6 +871,7 @@ func TestResolverRequestHandler_RequestShardHeaderByNonce(t *testing.T) {
 			1,
 			0,
 			time.Second,
+			time.Millisecond,
 		)
 
 		rrh.RequestShardHeaderByNonce(0, 0)
@@ -864,6 +897,7 @@ func TestResolverRequestHandler_RequestMetaHeaderByNonce(t *testing.T) {
 			1,
 			0,
 			time.Second,
+			time.Millisecond,
 		)
 
 		rrh.RequestMetaHeaderByNonce(0)
@@ -886,6 +920,7 @@ func TestResolverRequestHandler_RequestMetaHeaderByNonce(t *testing.T) {
 			100,
 			0,
 			time.Second,
+			time.Millisecond,
 		)
 
 		rrh.RequestMetaHeaderByNonce(0)
@@ -910,6 +945,7 @@ func TestResolverRequestHandler_RequestMetaHeaderByNonce(t *testing.T) {
 			100,
 			0,
 			time.Second,
+			time.Millisecond,
 		)
 
 		rrh.RequestMetaHeaderByNonce(0)
@@ -936,6 +972,7 @@ func TestResolverRequestHandler_RequestMetaHeaderByNonce(t *testing.T) {
 			100,
 			0,
 			time.Second,
+			time.Millisecond,
 		)
 
 		rrh.RequestMetaHeaderByNonce(0)
@@ -965,6 +1002,7 @@ func TestResolverRequestHandler_RequestScrErrorWhenGettingCrossShardRequesterSho
 		1,
 		0,
 		time.Second,
+		time.Millisecond,
 	)
 
 	rrh.RequestUnsignedTransactions(0, make([][]byte, 0))
@@ -993,6 +1031,7 @@ func TestResolverRequestHandler_RequestScrWrongResolverShouldNotPanic(t *testing
 		1,
 		0,
 		time.Second,
+		time.Millisecond,
 	)
 
 	rrh.RequestUnsignedTransactions(0, make([][]byte, 0))
@@ -1020,6 +1059,7 @@ func TestResolverRequestHandler_RequestScrShouldRequestScr(t *testing.T) {
 		1,
 		0,
 		time.Second,
+		time.Millisecond,
 	)
 
 	rrh.RequestUnsignedTransactions(0, [][]byte{[]byte("txHash")})
@@ -1062,6 +1102,7 @@ func TestResolverRequestHandler_RequestScrErrorsOnRequestShouldNotPanic(t *testi
 		1,
 		0,
 		time.Second,
+		time.Millisecond,
 	)
 
 	rrh.RequestUnsignedTransactions(0, [][]byte{[]byte("txHash")})
@@ -1097,6 +1138,7 @@ func TestResolverRequestHandler_RequestRewardShouldRequestReward(t *testing.T) {
 		1,
 		0,
 		time.Second,
+		time.Millisecond,
 	)
 
 	rrh.RequestRewardTransactions(0, [][]byte{[]byte("txHash")})
@@ -1135,6 +1177,7 @@ func TestRequestTrieNodes(t *testing.T) {
 			1,
 			0,
 			time.Second,
+			time.Millisecond,
 		)
 
 		rrh.RequestTrieNodes(0, [][]byte{[]byte("hash")}, "topic")
@@ -1163,6 +1206,7 @@ func TestRequestTrieNodes(t *testing.T) {
 			1,
 			0,
 			time.Second,
+			time.Millisecond,
 		)
 
 		rrh.RequestTrieNodes(core.MetachainShardId, [][]byte{[]byte("hash")}, "topic")
@@ -1183,6 +1227,7 @@ func TestRequestTrieNodes(t *testing.T) {
 			1,
 			0,
 			time.Second,
+			time.Millisecond,
 		)
 
 		rrh.RequestTrieNodes(core.MetachainShardId, [][]byte{}, "topic")
@@ -1211,6 +1256,7 @@ func TestResolverRequestHandler_RequestStartOfEpochMetaBlock(t *testing.T) {
 			1,
 			0,
 			time.Second,
+			time.Millisecond,
 		)
 
 		rrh.RequestStartOfEpochMetaBlock(0)
@@ -1231,6 +1277,7 @@ func TestResolverRequestHandler_RequestStartOfEpochMetaBlock(t *testing.T) {
 			1,
 			0,
 			time.Second,
+			time.Millisecond,
 		)
 
 		rrh.RequestStartOfEpochMetaBlock(0)
@@ -1252,6 +1299,7 @@ func TestResolverRequestHandler_RequestStartOfEpochMetaBlock(t *testing.T) {
 			1,
 			0,
 			time.Second,
+			time.Millisecond,
 		)
 
 		rrh.RequestStartOfEpochMetaBlock(0)
@@ -1279,6 +1327,7 @@ func TestResolverRequestHandler_RequestStartOfEpochMetaBlock(t *testing.T) {
 			1,
 			0,
 			time.Second,
+			time.Millisecond,
 		)
 
 		rrh.RequestStartOfEpochMetaBlock(0)
@@ -1310,6 +1359,7 @@ func TestResolverRequestHandler_RequestStartOfEpochMetaBlock(t *testing.T) {
 			1,
 			0,
 			time.Second,
+			time.Millisecond,
 		)
 
 		rrh.RequestStartOfEpochMetaBlock(0)
@@ -1338,6 +1388,7 @@ func TestResolverRequestHandler_RequestTrieNodeRequestFails(t *testing.T) {
 		1,
 		0,
 		time.Second,
+		time.Millisecond,
 	)
 
 	rrh.RequestTrieNode([]byte("hash"), "topic", 1)
@@ -1370,6 +1421,7 @@ func TestResolverRequestHandler_RequestTrieNodeShouldWork(t *testing.T) {
 		1,
 		0,
 		time.Second,
+		time.Millisecond,
 	)
 
 	rrh.RequestTrieNode([]byte("hash"), "topic", 1)
@@ -1397,6 +1449,7 @@ func TestResolverRequestHandler_RequestTrieNodeNilResolver(t *testing.T) {
 		1,
 		0,
 		time.Second,
+		time.Millisecond,
 	)
 
 	rrh.RequestTrieNode([]byte("hash"), "topic", 1)
@@ -1419,6 +1472,7 @@ func TestResolverRequestHandler_RequestTrieNodeNotAValidResolver(t *testing.T) {
 		1,
 		0,
 		time.Second,
+		time.Millisecond,
 	)
 
 	rrh.RequestTrieNode([]byte("hash"), "topic", 1)
@@ -1452,6 +1506,7 @@ func TestResolverRequestHandler_RequestPeerAuthenticationsByHashes(t *testing.T)
 			1,
 			0,
 			time.Second,
+			time.Millisecond,
 		)
 
 		rrh.RequestPeerAuthenticationsByHashes(providedShardId, providedHashes)
@@ -1473,6 +1528,7 @@ func TestResolverRequestHandler_RequestPeerAuthenticationsByHashes(t *testing.T)
 			1,
 			0,
 			time.Second,
+			time.Millisecond,
 		)
 
 		rrh.RequestPeerAuthenticationsByHashes(providedShardId, providedHashes)
@@ -1505,6 +1561,7 @@ func TestResolverRequestHandler_RequestPeerAuthenticationsByHashes(t *testing.T)
 			1,
 			0,
 			time.Second,
+			time.Millisecond,
 		)
 
 		rrh.RequestPeerAuthenticationsByHashes(providedShardId, providedHashes)
@@ -1540,6 +1597,7 @@ func TestResolverRequestHandler_RequestPeerAuthenticationsByHashes(t *testing.T)
 			1,
 			0,
 			time.Second,
+			time.Millisecond,
 		)
 
 		rrh.RequestPeerAuthenticationsByHashes(providedShardId, providedHashes)
@@ -1570,6 +1628,7 @@ func TestResolverRequestHandler_RequestValidatorInfo(t *testing.T) {
 			100,
 			0,
 			time.Second,
+			time.Millisecond,
 		)
 
 		rrh.RequestValidatorInfo(providedHash)
@@ -1597,6 +1656,7 @@ func TestResolverRequestHandler_RequestValidatorInfo(t *testing.T) {
 			100,
 			0,
 			time.Second,
+			time.Millisecond,
 		)
 
 		rrh.RequestValidatorInfo(providedHash)
@@ -1628,6 +1688,7 @@ func TestResolverRequestHandler_RequestValidatorInfo(t *testing.T) {
 			100,
 			0,
 			time.Second,
+			time.Millisecond,
 		)
 
 		rrh.RequestValidatorInfo(providedHash)
@@ -1657,6 +1718,7 @@ func TestResolverRequestHandler_RequestValidatorInfo(t *testing.T) {
 			100,
 			0,
 			time.Second,
+			time.Millisecond,
 		)
 
 		rrh.RequestValidatorInfo(providedHash)
@@ -1682,6 +1744,7 @@ func TestResolverRequestHandler_RequestValidatorsInfo(t *testing.T) {
 			100,
 			0,
 			time.Second,
+			time.Millisecond,
 		)
 
 		rrh.RequestValidatorsInfo([][]byte{})
@@ -1709,6 +1772,7 @@ func TestResolverRequestHandler_RequestValidatorsInfo(t *testing.T) {
 			100,
 			0,
 			time.Second,
+			time.Millisecond,
 		)
 
 		rrh.RequestValidatorsInfo([][]byte{providedHash})
@@ -1740,6 +1804,7 @@ func TestResolverRequestHandler_RequestValidatorsInfo(t *testing.T) {
 			100,
 			0,
 			time.Second,
+			time.Millisecond,
 		)
 
 		rrh.RequestValidatorsInfo([][]byte{providedHash})
@@ -1765,6 +1830,7 @@ func TestResolverRequestHandler_RequestValidatorsInfo(t *testing.T) {
 			100,
 			0,
 			time.Second,
+			time.Millisecond,
 		)
 
 		rrh.RequestValidatorsInfo([][]byte{providedHash})
@@ -1795,6 +1861,7 @@ func TestResolverRequestHandler_RequestValidatorsInfo(t *testing.T) {
 			100,
 			0,
 			time.Second,
+			time.Millisecond,
 		)
 
 		rrh.RequestValidatorsInfo(providedHashes)
@@ -1820,6 +1887,7 @@ func TestResolverRequestHandler_RequestMiniblocks(t *testing.T) {
 			100,
 			0,
 			time.Second,
+			time.Millisecond,
 		)
 
 		rrh.RequestMiniBlocks(0, [][]byte{})
@@ -1838,6 +1906,7 @@ func TestResolverRequestHandler_RequestMiniblocks(t *testing.T) {
 			100,
 			0,
 			time.Second,
+			time.Millisecond,
 		)
 
 		rrh.RequestMiniBlocks(0, [][]byte{[]byte("mbHash")})
@@ -1861,6 +1930,7 @@ func TestResolverRequestHandler_RequestMiniblocks(t *testing.T) {
 			100,
 			0,
 			time.Second,
+			time.Millisecond,
 		)
 
 		rrh.RequestMiniBlocks(0, [][]byte{[]byte("mbHash")})
@@ -1884,6 +1954,7 @@ func TestResolverRequestHandler_RequestMiniblocks(t *testing.T) {
 			100,
 			0,
 			time.Second,
+			time.Millisecond,
 		)
 
 		rrh.RequestMiniBlocks(0, [][]byte{[]byte("mbHash")})
@@ -1902,6 +1973,7 @@ func TestResolverRequestHandler_RequestMiniblocks(t *testing.T) {
 			100,
 			0,
 			time.Second,
+			time.Millisecond,
 		)
 
 		rrh.RequestMiniBlocks(0, [][]byte{[]byte("mbHash")})
@@ -1918,6 +1990,7 @@ func TestResolverRequestHandler_RequestInterval(t *testing.T) {
 		100,
 		0,
 		time.Second,
+		time.Millisecond,
 	)
 	require.Equal(t, time.Second, rrh.RequestInterval())
 }
@@ -1939,6 +2012,7 @@ func TestResolverRequestHandler_NumPeersToQuery(t *testing.T) {
 			100,
 			0,
 			time.Second,
+			time.Millisecond,
 		)
 
 		_, _, err := rrh.GetNumPeersToQuery("key")
@@ -1971,6 +2045,7 @@ func TestResolverRequestHandler_NumPeersToQuery(t *testing.T) {
 			100,
 			0,
 			time.Second,
+			time.Millisecond,
 		)
 
 		intra, cross, err := rrh.GetNumPeersToQuery("key")
@@ -1996,6 +2071,7 @@ func TestResolverRequestHandler_IsInterfaceNil(t *testing.T) {
 		100,
 		0,
 		time.Second,
+		time.Millisecond,
 	)
 	require.False(t, rrh.IsInterfaceNil())
 }
@@ -2027,6 +2103,7 @@ func TestResolverRequestHandler_RequestEquivalentProofByHash(t *testing.T) {
 			100,
 			0,
 			time.Second,
+			time.Millisecond,
 		)
 
 		rrh.RequestEquivalentProofByHash(core.MetachainShardId, providedHash)
@@ -2046,6 +2123,7 @@ func TestResolverRequestHandler_RequestEquivalentProofByHash(t *testing.T) {
 			100,
 			0,
 			time.Second,
+			time.Millisecond,
 		)
 
 		rrh.RequestEquivalentProofByHash(1, providedHash)
@@ -2069,6 +2147,7 @@ func TestResolverRequestHandler_RequestEquivalentProofByHash(t *testing.T) {
 			100,
 			core.MetachainShardId,
 			time.Second,
+			time.Millisecond,
 		)
 
 		rrh.RequestEquivalentProofByHash(core.MetachainShardId, providedHash)
@@ -2092,6 +2171,7 @@ func TestResolverRequestHandler_RequestEquivalentProofByHash(t *testing.T) {
 			100,
 			0,
 			time.Second,
+			time.Millisecond,
 		)
 
 		rrh.RequestEquivalentProofByHash(1, providedHash)
@@ -2119,6 +2199,7 @@ func TestResolverRequestHandler_RequestEquivalentProofByHash(t *testing.T) {
 			100,
 			core.MetachainShardId,
 			time.Second,
+			time.Millisecond,
 		)
 
 		rrh.RequestEquivalentProofByHash(core.MetachainShardId, providedHash)
@@ -2145,6 +2226,7 @@ func TestResolverRequestHandler_RequestEquivalentProofByHash(t *testing.T) {
 			100,
 			0,
 			time.Second,
+			time.Millisecond,
 		)
 
 		rrh.RequestEquivalentProofByHash(0, providedHash)
@@ -2175,6 +2257,7 @@ func TestResolverRequestHandler_RequestEquivalentProofByHash(t *testing.T) {
 			100,
 			core.MetachainShardId,
 			time.Second,
+			time.Millisecond,
 		)
 
 		rrh.RequestEquivalentProofByHash(core.MetachainShardId, providedHash)
@@ -2204,6 +2287,7 @@ func TestResolverRequestHandler_RequestEquivalentProofByHash(t *testing.T) {
 			100,
 			0,
 			time.Second,
+			time.Millisecond,
 		)
 
 		rrh.RequestEquivalentProofByHash(0, providedHash)
@@ -2234,6 +2318,7 @@ func TestResolverRequestHandler_RequestEquivalentProofByHash(t *testing.T) {
 			100,
 			core.MetachainShardId,
 			time.Second,
+			time.Millisecond,
 		)
 
 		rrh.RequestEquivalentProofByHash(0, providedHash)
```

### epochStart/bootstrap/epochStartMetaBlockProcessor.go
```diff
@@ -34,6 +34,7 @@ type epochStartMetaBlockProcessor struct {
 	hasher              hashing.Hasher
 	enableEpochsHandler common.EnableEpochsHandler
 	proofsPool          ProofsPool
+	headersPool         HeadersPool
 
 	mutReceivedMetaBlocks  sync.RWMutex
 	mapReceivedMetaBlocks  map[string]data.MetaHeaderHandler
@@ -59,6 +60,7 @@ func NewEpochStartMetaBlockProcessor(
 	minNumOfPeersToConsiderBlockValidConfig int,
 	enableEpochsHandler common.EnableEpochsHandler,
 	proofsPool ProofsPool,
+	headersPool HeadersPool,
 ) (*epochStartMetaBlockProcessor, error) {
 	if check.IfNil(messenger) {
 		return nil, epochStart.ErrNilMessenger
@@ -87,6 +89,9 @@ func NewEpochStartMetaBlockProcessor(
 	if check.IfNil(proofsPool) {
 		return nil, epochStart.ErrNilProofsPool
 	}
+	if check.IfNil(headersPool) {
+		return nil, epochStart.ErrNilHeadersDataPool
+	}
 
 	processor := &epochStartMetaBlockProcessor{
 		messenger:                         messenger,
@@ -102,6 +107,7 @@ func NewEpochStartMetaBlockProcessor(
 		chanMetaBlockProofReached:         make(chan bool, 1),
 		chanMetaBlockReached:              make(chan bool, 1),
 		proofsPool:                        proofsPool,
+		headersPool:                       headersPool,
 	}
 
 	proofsPool.RegisterHandler(processor.receivedProof)
@@ -207,6 +213,8 @@ func (e *epochStartMetaBlockProcessor) GetEpochStartMetaBlock(ctx context.Contex
 
 	e.requestHandler.SetEpoch(metaBlock.GetEpoch())
 	if e.enableEpochsHandler.IsFlagEnabledInEpoch(common.AndromedaFlag, metaBlock.GetEpoch()) {
+		e.headersPool.AddHeader([]byte(metaBlockHash), metaBlock)
+
 		err = e.waitForMetaBlockProof(ctx, []byte(metaBlockHash))
 		if err != nil {
 			return nil, err
```

### epochStart/bootstrap/epochStartMetaBlockProcessor_test.go
```diff
@@ -17,6 +17,7 @@ import (
 	"github.com/multiversx/mx-chain-go/testscommon/enableEpochsHandlerMock"
 	"github.com/multiversx/mx-chain-go/testscommon/hashingMocks"
 	"github.com/multiversx/mx-chain-go/testscommon/p2pmocks"
+	"github.com/multiversx/mx-chain-go/testscommon/pool"
 	"github.com/stretchr/testify/assert"
 )
 
@@ -33,6 +34,7 @@ func TestNewEpochStartMetaBlockProcessor_NilMessengerShouldErr(t *testing.T) {
 		3,
 		&enableEpochsHandlerMock.EnableEpochsHandlerStub{},
 		&dataRetriever.ProofsPoolMock{},
+		&pool.HeadersPoolStub{},
 	)
 
 	assert.Equal(t, epochStart.ErrNilMessenger, err)
@@ -52,6 +54,7 @@ func TestNewEpochStartMetaBlockProcessor_NilRequestHandlerShouldErr(t *testing.T
 		3,
 		&enableEpochsHandlerMock.EnableEpochsHandlerStub{},
 		&dataRetriever.ProofsPoolMock{},
+		&pool.HeadersPoolStub{},
 	)
 
 	assert.Equal(t, epochStart.ErrNilRequestHandler, err)
@@ -71,6 +74,7 @@ func TestNewEpochStartMetaBlockProcessor_NilMarshalizerShouldErr(t *testing.T) {
 		3,
 		&enableEpochsHandlerMock.EnableEpochsHandlerStub{},
 		&dataRetriever.ProofsPoolMock{},
+		&pool.HeadersPoolStub{},
 	)
 
 	assert.Equal(t, epochStart.ErrNilMarshalizer, err)
@@ -90,12 +94,53 @@ func TestNewEpochStartMetaBlockProcessor_NilHasherShouldErr(t *testing.T) {
 		3,
 		&enableEpochsHandlerMock.EnableEpochsHandlerStub{},
 		&dataRetriever.ProofsPoolMock{},
+		&pool.HeadersPoolStub{},
 	)
 
 	assert.Equal(t, epochStart.ErrNilHasher, err)
 	assert.True(t, check.IfNil(esmbp))
 }
 
+func TestNewEpochStartMetaBlockProcessor_NilProofsPoolShouldErr(t *testing.T) {
+	t.Parallel()
+
+	esmbp, err := NewEpochStartMetaBlockProcessor(
+		&p2pmocks.MessengerStub{},
+		&testscommon.RequestHandlerStub{},
+		&mock.MarshalizerMock{},
+		&hashingMocks.HasherMock{},
+		50,
+		3,
+		3,
+		&enableEpochsHandlerMock.EnableEpochsHandlerStub{},
+		nil,
+		&pool.HeadersPoolStub{},
+	)
+
+	assert.Equal(t, epochStart.ErrNilProofsPool, err)
+	assert.True(t, check.IfNil(esmbp))
+}
+
+func TestNewEpochStartMetaBlockProcessor_NilHeadersPoolShouldErr(t *testing.T) {
+	t.Parallel()
+
+	esmbp, err := NewEpochStartMetaBlockProcessor(
+		&p2pmocks.MessengerStub{},
+		&testscommon.RequestHandlerStub{},
+		&mock.MarshalizerMock{},
+		&hashingMocks.HasherMock{},
+		50,
+		3,
+		3,
+		&enableEpochsHandlerMock.EnableEpochsHandlerStub{},
+		&dataRetriever.ProofsPoolMock{},
+		nil,
+	)
+
+	assert.Equal(t, epochStart.ErrNilHeadersDataPool, err)
+	assert.True(t, check.IfNil(esmbp))
+}
+
 func TestNewEpochStartMetaBlockProcessor_InvalidConsensusPercentageShouldErr(t *testing.T) {
 	t.Parallel()
 
@@ -109,6 +154,7 @@ func TestNewEpochStartMetaBlockProcessor_InvalidConsensusPercentageShouldErr(t *
 		3,
 		&enableEpochsHandlerMock.EnableEpochsHandlerStub{},
 		&dataRetriever.ProofsPoolMock{},
+		&pool.HeadersPoolStub{},
 	)
 
 	assert.Equal(t, epochStart.ErrInvalidConsensusThreshold, err)
@@ -131,6 +177,7 @@ func TestNewEpochStartMetaBlockProcessorOkValsShouldWork(t *testing.T) {
 		3,
 		&enableEpochsHandlerMock.EnableEpochsHandlerStub{},
 		&dataRetriever.ProofsPoolMock{},
+		&pool.HeadersPoolStub{},
 	)
 
 	assert.NoError(t, err)
@@ -169,6 +216,7 @@ func TestNewEpochStartMetaBlockProcessorOkValsShouldWorkAfterMoreTriesWaitingFor
 		3,
 		&enableEpochsHandlerMock.EnableEpochsHandlerStub{},
 		&dataRetriever.ProofsPoolMock{},
+		&pool.HeadersPoolStub{},
 	)
 
 	assert.NoError(t, err)
@@ -191,6 +239,7 @@ func TestEpochStartMetaBlockProcessor_Validate(t *testing.T) {
 		3,
 		&enableEpochsHandlerMock.EnableEpochsHandlerStub{},
 		&dataRetriever.ProofsPoolMock{},
+		&pool.HeadersPoolStub{},
 	)
 
 	assert.Nil(t, esmbp.Validate(nil, ""))
@@ -212,6 +261,7 @@ func TestEpochStartMetaBlockProcessor_SaveNilInterceptedDataShouldNotReturnError
 		3,
 		&enableEpochsHandlerMock.EnableEpochsHandlerStub{},
 		&dataRetriever.ProofsPoolMock{},
+		&pool.HeadersPoolStub{},
 	)
 
 	err := esmbp.Save(nil, "peer0", "")
@@ -235,6 +285,7 @@ func TestEpochStartMetaBlockProcessor_SaveOkInterceptedDataShouldWork(t *testing
 		3,
 		&enableEpochsHandlerMock.EnableEpochsHandlerStub{},
 		&dataRetriever.ProofsPoolMock{},
+		&pool.HeadersPoolStub{},
 	)
 
 	assert.Zero(t, len(esmbp.GetMapMetaBlock()))
@@ -266,6 +317,7 @@ func TestEpochStartMetaBlockProcessor_GetEpochStartMetaBlockShouldTimeOut(t *tes
 		3,
 		&enableEpochsHandlerMock.EnableEpochsHandlerStub{},
 		&dataRetriever.ProofsPoolMock{},
+		&pool.HeadersPoolStub{},
 	)
 
 	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Millisecond)
@@ -292,6 +344,7 @@ func TestEpochStartMetaBlockProcessor_GetEpochStartMetaBlockShouldReturnMostRece
 		5,
 		&enableEpochsHandlerMock.EnableEpochsHandlerStub{},
 		&dataRetriever.ProofsPoolMock{},
+		&pool.HeadersPoolStub{},
 	)
 
 	expectedMetaBlock := &block.MetaBlock{
@@ -338,6 +391,7 @@ func TestEpochStartMetaBlockProcessor_GetEpochStartMetaBlockShouldWorkFromFirstT
 		3,
 		&enableEpochsHandlerMock.EnableEpochsHandlerStub{},
 		&dataRetriever.ProofsPoolMock{},
+		&pool.HeadersPoolStub{},
 	)
 
 	expectedMetaBlock := &block.MetaBlock{
@@ -384,6 +438,7 @@ func TestEpochStartMetaBlockProcessor_GetEpochStartMetaBlock_BeforeAndromeda(t *
 		3,
 		&enableEpochsHandlerMock.EnableEpochsHandlerStub{},
 		&dataRetriever.ProofsPoolMock{},
+		&pool.HeadersPoolStub{},
 	)
 	expectedMetaBlock := &block.MetaBlock{
 		Nonce:      10,
@@ -435,6 +490,7 @@ func TestEpochStartMetaBlockProcessor_GetEpochStartMetaBlock_AfterAndromeda(t *t
 				return true
 			},
 		},
+		&pool.HeadersPoolStub{},
 	)
 	expectedMetaBlock := &block.MetaBlock{
 		Nonce:      10,
```

### epochStart/bootstrap/interface.go
```diff
@@ -73,3 +73,9 @@ type ProofsPool interface {
 	HasProof(shardID uint32, headerHash []byte) bool
 	IsInterfaceNil() bool
 }
+
+// HeadersPool defines what a headers pool structure can perform
+type HeadersPool interface {
+	AddHeader(headerHash []byte, header data.HeaderHandler)
+	IsInterfaceNil() bool
+}
```

### epochStart/bootstrap/process.go
```diff
@@ -561,6 +561,7 @@ func (e *epochStartBootstrap) prepareComponentsToSyncFromNetwork() error {
 		epochStartConfig.MinNumOfPeersToConsiderBlockValid,
 		e.enableEpochsHandler,
 		e.dataPool.Proofs(),
+		e.dataPool.Headers(),
 	)
 	if err != nil {
 		return err
@@ -579,6 +580,7 @@ func (e *epochStartBootstrap) prepareComponentsToSyncFromNetwork() error {
 		MetaBlockProcessor:             metaBlockProcessor,
 		InterceptedDataVerifierFactory: e.interceptedDataVerifierFactory,
 		ProofsPool:                     e.dataPool.Proofs(),
+		HeadersPool:                    e.dataPool.Headers(),
 		ProofsInterceptorProcessor:     processor.NewEquivalentProofsInterceptorProcessor(),
 	}
 	e.epochStartMetaBlockSyncer, err = NewEpochStartMetaSyncer(argsEpochStartSyncer)
@@ -1535,6 +1537,7 @@ func (e *epochStartBootstrap) createRequestHandler() error {
 		maxToRequest,
 		core.MetachainShardId,
 		timeBetweenRequests,
+		time.Duration(e.generalConfig.Requesters.RequestProofByNonceDelayMs)*time.Millisecond,
 	)
 	return err
 }
```

### epochStart/bootstrap/storageProcess.go
```diff
@@ -191,6 +191,7 @@ func (sesb *storageEpochStartBootstrap) prepareComponentsToSync() error {
 		MetaBlockProcessor:             metablockProcessor,
 		InterceptedDataVerifierFactory: sesb.interceptedDataVerifierFactory,
 		ProofsPool:                     sesb.dataPool.Proofs(),
+		HeadersPool:                    sesb.dataPool.Headers(),
 		ProofsInterceptorProcessor:     processor.NewEquivalentProofsInterceptorProcessor(),
 	}
 
@@ -221,6 +222,7 @@ func (sesb *storageEpochStartBootstrap) createStorageRequestHandler() error {
 		maxToRequest,
 		core.MetachainShardId,
 		timeBetweenRequests,
+		time.Duration(sesb.generalConfig.Requesters.RequestProofByNonceDelayMs)*time.Millisecond,
 	)
 	return err
 }
```

### epochStart/bootstrap/syncEpochStartMeta.go
```diff
@@ -50,6 +50,7 @@ type ArgsNewEpochStartMetaSyncer struct {
 	MetaBlockProcessor             EpochStartMetaBlockInterceptorProcessor
 	InterceptedDataVerifierFactory process.InterceptedDataVerifierFactory
 	ProofsPool                     dataRetriever.ProofsPool
+	HeadersPool                    dataRetriever.HeadersPool
 	ProofsInterceptorProcessor     process.InterceptorProcessor
 }
 
@@ -97,6 +98,7 @@ func NewEpochStartMetaSyncer(args ArgsNewEpochStartMetaSyncer) (*epochStartMetaS
 		ValidityAttester:        disabled.NewValidityAttester(),
 		EpochStartTrigger:       disabled.NewEpochStartTrigger(),
 		ArgsParser:              args.ArgsParser,
+		ProofsPool:              args.ProofsPool,
 	}
 	argsInterceptedMetaHeaderFactory := interceptorsFactory.ArgInterceptedMetaHeaderFactory{
 		ArgInterceptedDataFactory: argsInterceptedDataFactory,
@@ -132,6 +134,7 @@ func NewEpochStartMetaSyncer(args ArgsNewEpochStartMetaSyncer) (*epochStartMetaS
 	argsInterceptedEquivalentProofsFactory := interceptorsFactory.ArgInterceptedEquivalentProofsFactory{
 		ArgInterceptedDataFactory: argsInterceptedDataFactory,
 		ProofsPool:                args.ProofsPool,
+		HeadersPool:               args.HeadersPool,
 	}
 	interceptedEquivalentProofsFactory := interceptorsFactory.NewInterceptedEquivalentProofsFactory(argsInterceptedEquivalentProofsFactory)
 	if err != nil {
```

### epochStart/bootstrap/syncEpochStartMeta_test.go
```diff
@@ -9,6 +9,7 @@ import (
 	"github.com/multiversx/mx-chain-core-go/core/check"
 	"github.com/multiversx/mx-chain-core-go/data"
 	"github.com/multiversx/mx-chain-core-go/data/block"
+	"github.com/multiversx/mx-chain-go/testscommon/pool"
 	"github.com/stretchr/testify/assert"
 	"github.com/stretchr/testify/require"
 
@@ -176,6 +177,7 @@ func getEpochStartSyncerArgs() ArgsNewEpochStartMetaSyncer {
 		MetaBlockProcessor:             &mock.EpochStartMetaBlockProcessorStub{},
 		InterceptedDataVerifierFactory: &processMock.InterceptedDataVerifierFactoryMock{},
 		ProofsPool:                     &dataRetriever.ProofsPoolMock{},
+		HeadersPool:                    &pool.HeadersPoolStub{},
 		ProofsInterceptorProcessor:     &processMock.InterceptorProcessorStub{},
 	}
 }
```
