# [?] Merge branch 'master' into fix-stopandwait-deadlock

## Summary
Severity: Unknown
Chain: Arbitrum
Component: OffchainLabs/nitro
Published: 2025-03-07
Source: https://github.com/OffchainLabs/nitro/commit/ef8f7bb6cbd293b24c0898072e1255a200f8eac0
Type: security-commit

## Details
Merge branch 'master' into fix-stopandwait-deadlock

## Patch
### arbnode/batch_poster.go
```diff
@@ -97,7 +97,7 @@ type BatchPoster struct {
 	l1Reader           *headerreader.HeaderReader
 	inbox              *InboxTracker
 	streamer           *TransactionStreamer
-	arbOSVersionGetter execution.FullExecutionClient
+	arbOSVersionGetter execution.ExecutionBatchPoster
 	config             BatchPosterConfigFetcher
 	seqInbox           *bridgegen.SequencerInbox
 	syncMonitor        *SyncMonitor
@@ -307,7 +307,7 @@ type BatchPosterOpts struct {
 	L1Reader      *headerreader.HeaderReader
 	Inbox         *InboxTracker
 	Streamer      *TransactionStreamer
-	VersionGetter execution.FullExecutionClient
+	VersionGetter execution.ExecutionBatchPoster
 	SyncMonitor   *SyncMonitor
 	Config        BatchPosterConfigFetcher
 	DeployInfo    *chaininfo.RollupAddresses
@@ -800,10 +800,18 @@ func (s *batchSegments) recompressAll() error {
 func (s *batchSegments) testForOverflow(isHeader bool) (bool, error) {
 	// we've reached the max decompressed size
 	if s.totalUncompressedSize > arbstate.MaxDecompressedLen {
+		log.Info("Batch full: max decompressed length exceeded",
+			"current", s.totalUncompressedSize,
+			"max", arbstate.MaxDecompressedLen,
+			"isHeader", isHeader)
 		return true, nil
 	}
 	// we've reached the max number of segments
 	if len(s.rawSegments) >= arbstate.MaxSegmentsPerSequencerMessage {
+		log.Info("Batch overflow: max segments exceeded",
+			"segments", len(s.rawSegments),
+			"max", arbstate.MaxSegmentsPerSequencerMessage,
+			"isHeader", isHeader)
 		return true, nil
 	}
 	// there is room, no need to flush
@@ -821,6 +829,10 @@ func (s *batchSegments) testForOverflow(isHeader bool) (bool, error) {
 	s.lastCompressedSize = s.compressedBuffer.Len()
 	s.newUncompressedSize = 0
 	if s.lastCompressedSize >= s.sizeLimit {
+		log.Info("Batch overflow: compressed size limit exceeded",
+			"compressedSize", s.lastCompressedSize,
+			"limit", s.sizeLimit,
+			"isHeader", isHeader)
 		return true, nil
 	}
 	return false, nil
```

### arbnode/blockmetadata.go
```diff
@@ -55,7 +55,7 @@ func NewBlockMetadataFetcher(ctx context.Context, c BlockMetadataFetcherConfig,
 	var trackBlockMetadataFrom arbutil.MessageIndex
 	var err error
 	if startPos != 0 {
-		trackBlockMetadataFrom, err = exec.BlockNumberToMessageIndex(startPos)
+		trackBlockMetadataFrom, err = exec.BlockNumberToMessageIndex(startPos).Await(ctx)
 		if err != nil {
 			return nil, err
 		}
@@ -83,11 +83,11 @@ func (b *BlockMetadataFetcher) fetch(ctx context.Context, fromBlock, toBlock uin
 	return result, nil
 }
 
-func (b *BlockMetadataFetcher) persistBlockMetadata(query []uint64, result []gethexec.NumberAndBlockMetadata) error {
+func (b *BlockMetadataFetcher) persistBlockMetadata(ctx context.Context, query []uint64, result []gethexec.NumberAndBlockMetadata) error {
 	batch := b.db.NewBatch()
 	queryMap := util.ArrayToSet(query)
 	for _, elem := range result {
-		pos, err := b.exec.BlockNumberToMessageIndex(elem.BlockNumber)
+		pos, err := b.exec.BlockNumberToMessageIndex(elem.BlockNumber).Await(ctx)
 		if err != nil {
 			return err
 		}
@@ -112,16 +112,27 @@ func (b *BlockMetadataFetcher) persistBlockMetadata(query []uint64, result []get
 
 func (b *BlockMetadataFetcher) Update(ctx context.Context) time.Duration {
 	handleQuery := func(query []uint64) bool {
+		fromBlock, err := b.exec.MessageIndexToBlockNumber(arbutil.MessageIndex(query[0])).Await(ctx)
+		if err != nil {
+			log.Error("Error getting fromBlock", "err", err)
+			return false
+		}
+		toBlock, err := b.exec.MessageIndexToBlockNumber(arbutil.MessageIndex(query[len(query)-1])).Await(ctx)
+		if err != nil {
+			log.Error("Error getting toBlock", "err", err)
+			return false
+		}
+
 		result, err := b.fetch(
 			ctx,
-			b.exec.MessageIndexToBlockNumber(arbutil.MessageIndex(query[0])),
-			b.exec.MessageIndexToBlockNumber(arbutil.MessageIndex(query[len(query)-1])),
+			fromBlock,
+			toBlock,
 		)
 		if err != nil {
 			log.Error("Error getting result from bulk blockMetadata API", "err", err)
 			return false
 		}
-		if err = b.persistBlockMetadata(query, result); err != nil {
+		if err = b.persistBlockMetadata(ctx, query, result); err != nil {
 			log.Error("Error committing result from bulk blockMetadata API to ArbDB", "err", err)
 			return false
 		}
```

### arbnode/consensus_execution_syncer.go
```diff
@@ -63,7 +63,7 @@ func (c *ConsensusExecutionSyncer) Start(ctx_in context.Context) {
 func (c *ConsensusExecutionSyncer) pushFinalityDataFromConsensusToExecution(ctx context.Context) time.Duration {
 	safeMsgCount, err := c.inboxReader.GetSafeMsgCount(ctx)
 	if errors.Is(err, headerreader.ErrBlockNumberNotSupported) {
-		log.Warn("Finality not supported, not pushing finality data to execution")
+		log.Info("Finality not supported, not pushing finality data to execution")
 		return c.config().SyncInterval
 	} else if err != nil {
 		log.Error("Error getting safe message count", "err", err)
@@ -72,7 +72,7 @@ func (c *ConsensusExecutionSyncer) pushFinalityDataFromConsensusToExecution(ctx
 
 	finalizedMsgCount, err := c.inboxReader.GetFinalizedMsgCount(ctx)
 	if errors.Is(err, headerreader.ErrBlockNumberNotSupported) {
-		log.Warn("Finality not supported, not pushing finality data to execution")
+		log.Info("Finality not supported, not pushing finality data to execution")
 		return c.config().SyncInterval
 	} else if err != nil {
 		log.Error("Error getting finalized message count", "err", err)
@@ -90,11 +90,11 @@ func (c *ConsensusExecutionSyncer) pushFinalityDataFromConsensusToExecution(ctx
 		ValidatedMsgCount: &validatedMsgCount,
 	}
 
-	err = c.execClient.SetFinalityData(ctx, finalityData)
+	_, err = c.execClient.SetFinalityData(ctx, finalityData).Await(ctx)
 	if err != nil {
 		log.Error("Error pushing finality data from consensus to execution", "err", err)
 	} else {
-		log.Info("Pushed finality data from consensus to execution", "finalityData", finalityData)
+		log.Info("Pushed finality data from consensus to execution", "SafeMsgCount", safeMsgCount, "FinalizedMsgCount", finalizedMsgCount, "ValidatedMsgCount", validatedMsgCount)
 	}
 
 	return c.config().SyncInterval
```

### arbnode/delayed_seq_reorg_test.go
```diff
@@ -19,7 +19,7 @@ func TestSequencerReorgFromDelayed(t *testing.T) {
 	ctx, cancel := context.WithCancel(context.Background())
 	defer cancel()
 
-	exec, streamer, db, _ := NewTransactionStreamerForTest(t, common.Address{})
+	exec, streamer, db, _ := NewTransactionStreamerForTest(t, ctx, common.Address{})
 	tracker, err := NewInboxTracker(db, streamer, nil, DefaultSnapSyncConfig)
 	Require(t, err)
 
@@ -219,7 +219,7 @@ func TestSequencerReorgFromLastDelayedMsg(t *testing.T) {
 	ctx, cancel := context.WithCancel(context.Background())
 	defer cancel()
 
-	exec, streamer, db, _ := NewTransactionStreamerForTest(t, common.Address{})
+	exec, streamer, db, _ := NewTransactionStreamerForTest(t, ctx, common.Address{})
 	tracker, err := NewInboxTracker(db, streamer, nil, DefaultSnapSyncConfig)
 	Require(t, err)
 
```

### arbnode/inbox_test.go
```diff
@@ -23,32 +23,89 @@ import (
 	"github.com/offchainlabs/nitro/arbos/l2pricing"
 	"github.com/offchainlabs/nitro/arbutil"
 	"github.com/offchainlabs/nitro/cmd/chaininfo"
+	"github.com/offchainlabs/nitro/execution"
 	"github.com/offchainlabs/nitro/execution/gethexec"
 	"github.com/offchainlabs/nitro/statetransfer"
 	"github.com/offchainlabs/nitro/util/arbmath"
+	"github.com/offchainlabs/nitro/util/containers"
 	"github.com/offchainlabs/nitro/util/testhelpers"
 	"github.com/offchainlabs/nitro/util/testhelpers/env"
 )
 
 type execClientWrapper struct {
-	*gethexec.ExecutionEngine
-	t *testing.T
+	ExecutionEngine *gethexec.ExecutionEngine
+	t               *testing.T
 }
 
-func (w *execClientWrapper) Pause()                     { w.t.Error("not supported") }
-func (w *execClientWrapper) Activate()                  { w.t.Error("not supported") }
+func (w *execClientWrapper) Pause() { w.t.Error("not supported") }
+
+func (w *execClientWrapper) Activate() { w.t.Error("not supported") }
+
 func (w *execClientWrapper) ForwardTo(url string) error { w.t.Error("not supported"); return nil }
-func (w *execClientWrapper) Synced() bool               { w.t.Error("not supported"); return false }
+
+func (w *execClientWrapper) SequenceDelayedMessage(message *arbostypes.L1IncomingMessage, delayedSeqNum uint64) error {
+	return w.ExecutionEngine.SequenceDelayedMessage(message, delayedSeqNum)
+}
+
+func (w *execClientWrapper) NextDelayedMessageNumber() (uint64, error) {
+	return w.ExecutionEngine.NextDelayedMessageNumber()
+}
+
+func (w *execClientWrapper) MarkFeedStart(to arbutil.MessageIndex) containers.PromiseInterface[struct{}] {
+	markFeedStartWithReturn := func(to arbutil.MessageIndex) (struct{}, error) {
+		w.ExecutionEngine.MarkFeedStart(to)
+		return struct{}{}, nil
+	}
+	return containers.NewReadyPromise(markFeedStartWithReturn(to))
+}
+
+func (w *execClientWrapper) Maintenance() containers.PromiseInterface[struct{}] {
+	return containers.NewReadyPromise(struct{}{}, nil)
+}
+
+func (w *execClientWrapper) Synced() bool { w.t.Error("not supported"); return false }
+
 func (w *execClientWrapper) FullSyncProgressMap() map[string]interface{} {
 	w.t.Error("not supported")
 	return nil
 }
-func (w *execClientWrapper) SetFinalityData(ctx context.Context, finalityData *arbutil.FinalityData) error {
-	w.t.Error("not supported")
-	return nil
+func (w *execClientWrapper) SetFinalityData(ctx context.Context, finalityData *arbutil.FinalityData) containers.PromiseInterface[struct{}] {
+	return containers.NewReadyPromise(struct{}{}, nil)
+}
+
+func (w *execClientWrapper) DigestMessage(num arbutil.MessageIndex, msg *arbostypes.MessageWithMetadata, msgForPrefetch *arbostypes.MessageWithMetadata) containers.PromiseInterface[*execution.MessageResult] {
+	return containers.NewReadyPromise(w.ExecutionEngine.DigestMessage(num, msg, msgForPrefetch))
 }
 
-func NewTransactionStreamerForTest(t *testing.T, ownerAddress common.Address) (*gethexec.ExecutionEngine, *TransactionStreamer, ethdb.Database, *core.BlockChain) {
+func (w *execClientWrapper) Reorg(count arbutil.MessageIndex, newMessages []arbostypes.MessageWithMetadataAndBlockInfo, oldMessages []*arbostypes.MessageWithMetadata) containers.PromiseInterface[[]*execution.MessageResult] {
+	return containers.NewReadyPromise(w.ExecutionEngine.Reorg(count, newMessages, oldMessages))
+}
+
+func (w *execClientWrapper) HeadMessageNumber() containers.PromiseInterface[arbutil.MessageIndex] {
+	return containers.NewReadyPromise(w.ExecutionEngine.HeadMessageNumber())
+}
+
+func (w *execClientWrapper) ResultAtPos(pos arbutil.MessageIndex) containers.PromiseInterface[*execution.MessageResult] {
+	return containers.NewReadyPromise(w.ExecutionEngine.ResultAtPos(pos))
+}
+
+func (w *execClientWrapper) Start(ctx context.Context) containers.PromiseInterface[struct{}] {
+	return containers.NewReadyPromise(struct{}{}, nil)
+}
+
+func (w *execClientWrapper) MessageIndexToBlockNumber(messageNum arbutil.MessageIndex) containers.PromiseInterface[uint64] {
+	return containers.NewReadyPromise(w.ExecutionEngine.MessageIndexToBlockNumber(messageNum), nil)
+}
+
+func (w *execClientWrapper) BlockNumberToMessageIndex(blockNum uint64) containers.PromiseInterface[arbutil.MessageIndex] {
+	return containers.NewReadyPromise(w.ExecutionEngine.BlockNumberToMessageIndex(blockNum))
+}
+
+func (w *execClientWrapper) StopAndWait() containers.PromiseInterface[struct{}] {
+	return containers.NewReadyPromise(struct{}{}, nil)
+}
+
+func NewTransactionStreamerForTest(t *testing.T, ctx context.Context, ownerAddress common.Address) (*gethexec.ExecutionEngine, *TransactionStreamer, ethdb.Database, *core.BlockChain) {
 	chainConfig := chaininfo.ArbitrumDevTestChainConfig()
 
 	initData := statetransfer.ArbosInitializationInfo{
@@ -82,7 +139,7 @@ func NewTransactionStreamerForTest(t *testing.T, ownerAddress common.Address) (*
 		Fail(t, err)
 	}
 	execSeq := &execClientWrapper{execEngine, t}
-	inbox, err := NewTransactionStreamer(arbDb, bc.Config(), execSeq, nil, make(chan error, 1), transactionStreamerConfigFetcher, &DefaultSnapSyncConfig)
+	inbox, err := NewTransactionStreamer(ctx, arbDb, bc.Config(), execSeq, nil, make(chan error, 1), transactionStreamerConfigFetcher, &DefaultSnapSyncConfig)
 	if err != nil {
 		Fail(t, err)
 	}
@@ -106,10 +163,11 @@ type blockTestState struct {
 func TestTransactionStreamer(t *testing.T) {
 	ownerAddress := common.HexToAddress("0x1111111111111111111111111111111111111111")
 
-	exec, inbox, _, bc := NewTransactionStreamerForTest(t, ownerAddress)
-
 	ctx, cancel := context.WithCancel(context.Background())
 	defer cancel()
+
+	exec, inbox, _, bc := NewTransactionStreamerForTest(t, ctx, ownerAddress)
+
 	err := inbox.Start(ctx)
 	Require(t, err)
 	exec.Start(ctx)
```

### arbnode/maintenance.go
```diff
@@ -26,7 +26,7 @@ import (
 type MaintenanceRunner struct {
 	stopwaiter.StopWaiter
 
-	exec            execution.FullExecutionClient
+	exec            execution.ExecutionClient
 	config          MaintenanceConfigFetcher
 	seqCoordinator  *SeqCoordinator
 	dbs             []ethdb.Database
@@ -92,7 +92,7 @@ var DefaultMaintenanceConfig = MaintenanceConfig{
 
 type MaintenanceConfigFetcher func() *MaintenanceConfig
 
-func NewMaintenanceRunner(config MaintenanceConfigFetcher, seqCoordinator *SeqCoordinator, dbs []ethdb.Database, exec execution.FullExecutionClient) (*MaintenanceRunner, error) {
+func NewMaintenanceRunner(config MaintenanceConfigFetcher, seqCoordinator *SeqCoordinator, dbs []ethdb.Database, exec execution.ExecutionClient) (*MaintenanceRunner, error) {
 	cfg := config()
 	if err := cfg.Validate(); err != nil {
 		return nil, fmt.Errorf("validating config: %w", err)
@@ -258,7 +258,8 @@ func (mr *MaintenanceRunner) runMaintenance() error {
 	}
 	expected++
 	go func() {
-		results <- mr.exec.Maintenance()
+		_, res := mr.exec.Maintenance().Await(mr.GetContext())
+		results <- res
 	}()
 	for i := 0; i < expected; i++ {
 		subErr := <-results
```

### arbnode/node.go
```diff
@@ -191,8 +191,8 @@ var ConfigDefault = Config{
 	Dangerous:                DefaultDangerousConfig,
 	TransactionStreamer:      DefaultTransactionStreamerConfig,
 	ResourceMgmt:             resourcemanager.DefaultConfig,
-	Maintenance:              DefaultMaintenanceConfig,
 	BlockMetadataFetcher:     DefaultBlockMetadataFetcherConfig,
+	Maintenance:              DefaultMaintenanceConfig,
 	ConsensusExecutionSyncer: DefaultConsensusExecutionSyncerConfig,
 	SnapSyncTest:             DefaultSnapSyncConfig,
 }
@@ -272,7 +272,9 @@ func DangerousConfigAddOptions(prefix string, f *flag.FlagSet) {
 type Node struct {
 	ArbDB                    ethdb.Database
 	Stack                    *node.Node
-	Execution                execution.FullExecutionClient
+	ExecutionClient          execution.ExecutionClient
+	ExecutionSequencer       execution.ExecutionSequencer
+	ExecutionRecorder        execution.ExecutionRecorder
 	L1Reader                 *headerreader.HeaderReader
 	TxStreamer               *TransactionStreamer
 	DeployInfo               *chaininfo.RollupAddresses
@@ -423,45 +425,38 @@ func StakerDataposter(
 		})
 }
 
-func createNodeImpl(
-	ctx context.Context,
-	stack *node.Node,
-	exec execution.FullExecutionClient,
-	arbDb ethdb.Database,
-	configFetcher ConfigFetcher,
-	l2Config *params.ChainConfig,
-	l1client *ethclient.Client,
-	deployInfo *chaininfo.RollupAddresses,
-	txOptsValidator *bind.TransactOpts,
-	txOptsBatchPoster *bind.TransactOpts,
-	dataSigner signature.DataSignerFunc,
-	fatalErrChan chan error,
-	parentChainID *big.Int,
-	blobReader daprovider.BlobReader,
-) (*Node, error) {
-	config := configFetcher.Get()
-
-	err := checkArbDbSchemaVersion(arbDb)
-	if err != nil {
-		return nil, err
-	}
-
-	l2ChainId := l2Config.ChainID.Uint64()
-
+func getSyncMonitor(configFetcher ConfigFetcher) *SyncMonitor {
 	syncConfigFetcher := func() *SyncMonitorConfig {
 		return &configFetcher.Get().SyncMonitor
 	}
-	syncMonitor := NewSyncMonitor(syncConfigFetcher)
+	return NewSyncMonitor(syncConfigFetcher)
+}
 
+func getL1Reader(
+	ctx context.Context,
+	config *Config,
+	configFetcher ConfigFetcher,
+	l1client *ethclient.Client,
+) (*headerreader.HeaderReader, error) {
 	var l1Reader *headerreader.HeaderReader
 	if config.ParentChainReader.Enable {
 		arbSys, _ := precompilesgen.NewArbSys(types.ArbSysAddress, l1client)
+		var err error
 		l1Reader, err = headerreader.New(ctx, l1client, func() *headerreader.Config { return &configFetcher.Get().ParentChainReader }, arbSys)
 		if err != nil {
 			return nil, err
 		}
 	}
+	return l1Reader, nil
+}
 
+func getBroadcastServer(
+	config *Config,
+	configFetcher ConfigFetcher,
+	dataSigner signature.DataSignerFunc,
+	l2ChainId uint64,
+	fatalErrChan chan error,
+) (*broadcaster.Broadcaster, error) {
 	var broadcastServer *broadcaster.Broadcaster
 	if config.Feed.Output.Enable {
 		var maybeDataSigner signature.DataSignerFunc
@@ -473,13 +468,13 @@ func createNodeImpl(
 		}
 		broadcastServer = broadcaster.NewBroadcaster(func() *wsbroadcastserver.BroadcasterConfig { return &configFetcher.Get().Feed.Output }, l2ChainId, fatalErrChan, maybeDataSigner)
 	}
+	return broadcastServer, nil
+}
 
-	transactionStreamerConfigFetcher := func() *TransactionStreamerConfig { return &configFetcher.Get().TransactionStreamer }
-	txStreamer, err := NewTransactionStreamer(arbDb, l2Config, exec, broadcastServer, fatalErrChan, transactionStreamerConfigFetcher, &configFetcher.Get().SnapSyncTest)
-	if err != nil {
-		return nil, err
-	}
-	var coordinator *SeqCoordinator
+func getBPVerifier(
+	deployInfo *chaininfo.RollupAddresses,
+	l1client *ethclient.Client,
+) (*contracts.AddressVerifier, error) {
 	var bpVerifier *contracts.AddressVerifier
 	if deployInfo != nil && l1client != nil {
 		sequencerInboxAddr := deployInfo.SequencerInbox
@@ -490,21 +485,31 @@ func createNodeImpl(
 		}
 		bpVerifier = contracts.NewAddressVerifier(seqInboxCaller)
 	}
+	return bpVerifier, nil
+}
 
-	if config.SeqCoordinator.Enable {
-		coordinator, err = NewSeqCoordinator(dataSigner, bpVerifier, txStreamer, exec, syncMonitor, config.SeqCoordinator)
-		if err != nil {
-			return nil, err
-		}
-	} else if config.Sequencer && !config.Dangerous.NoSequencerCoordinator {
-		return nil, errors.New("sequencer must be enabled with coordinator, unless dangerous.no-sequencer-coordinator set")
-	}
+func getMaintenanceRunner(
+	arbDb ethdb.Database,
+	configFetcher ConfigFetcher,
+	coordinator *SeqCoordinator,
+	exec execution.ExecutionClient,
+) (*MaintenanceRunner, error) {
 	dbs := []ethdb.Database{arbDb}
 	maintenanceRunner, err := NewMaintenanceRunner(func() *MaintenanceConfig { return &configFetcher.Get().Maintenance }, coordinator, dbs, exec)
 	if err != nil {
 		return nil, err
 	}
+	return maintenanceRunner, nil
+}
 
+func getBroadcastClients(
+	config *Config,
+	configFetcher ConfigFetcher,
+	txStreamer *TransactionStreamer,
+	l2ChainId uint64,
+	bpVerifier *contracts.AddressVerifier,
+	fatalErrChan chan error,
+) (*broadcastclients.BroadcastClients, error) {
 	var broadcastClients *broadcastclients.BroadcastClients
 	if config.Feed.Input.Enable() {
 		currentMessageCount, err := txStreamer.GetMessageCount()
@@ -525,71 +530,73 @@ func createNodeImpl(
 			return nil, err
 		}
 	}
+	return broadcastClients, nil
+}
+
+func getBlockMetadataFetcher(
+	ctx context.Context,
+	configFetcher ConfigFetcher,
+	arbDb ethdb.Database,
+	exec execution.ExecutionClient,
+) (*BlockMetadataFetcher, error) {
+	config := configFetcher.Get()
 
 	var blockMetadataFetcher *BlockMetadataFetcher
 	if config.BlockMetadataFetcher.Enable {
+		var err error
 		blockMetadataFetcher, err = NewBlockMetadataFetcher(ctx, config.BlockMetadataFetcher, arbDb, exec, config.TransactionStreamer.TrackBlockMetadataFrom)
 		if err != nil {
 			return nil, err
 		}
 	}
+	return blockMetadataFetcher, nil
+}
 
-	if !config.ParentChainReader.Enable {
-		return &Node{
-			ArbDB:                   arbDb,
-			Stack:                   stack,
-			Execution:               exec,
-			L1Reader:                nil,
-			TxStreamer:              txStreamer,
-			DeployInfo:              nil,
-			BlobReader:              blobReader,
-			InboxReader:             nil,
-			InboxTracker:            nil,
-			DelayedSequencer:        nil,
-			BatchPoster:             nil,
-			MessagePruner:           nil,
-			BlockValidator:          nil,
-			StatelessBlockValidator: nil,
-			Staker:                  nil,
-			BroadcastServer:         broadcastServer,
-			BroadcastClients:        broadcastClients,
-			SeqCoordinator:          coordinator,
-			MaintenanceRunner:       maintenanceRunner,
-			DASLifecycleManager:     nil,
-			SyncMonitor:             syncMonitor,
-			blockMetadataFetcher:    blockMetadataFetcher,
-			configFetcher:           configFetcher,
-			ctx:                     ctx,
-		}, nil
-	}
-
+func getDelayedBridgeAndSequencerInbox(
+	deployInfo *chaininfo.RollupAddresses,
+	l1client *ethclient.Client,
+) (*DelayedBridge, *SequencerInbox, error) {
 	if deployInfo == nil {
-		return nil, errors.New("deployinfo is nil")
+		return nil, nil, errors.New("deployinfo is nil")
 	}
 	delayedBridge, err := NewDelayedBridge(l1client, deployInfo.Bridge, deployInfo.DeployedAt)
 	if err != nil {
-		return nil, err
+		return nil, nil, err
 	}
 	// #nosec G115
 	sequencerInbox, err := NewSequencerInbox(l1client, deployInfo.SequencerInbox, int64(deployInfo.DeployedAt))
 	if err != nil {
-		return nil, err
+		return nil, nil, err
 	}
+	return delayedBridge, sequencerInbox, nil
+}
 
+func getDAS(
+	ctx context.Context,
+	config *Config,
+	l2Config *params.ChainConfig,
+	txStreamer *TransactionStreamer,
+	blobReader daprovider.BlobReader,
+	l1Reader *headerreader.HeaderReader,
+	deployInfo *chaininfo.RollupAddresses,
+	dataSigner signature.DataSignerFunc,
+	l1client *ethclient.Client,
+) (das.DataAvailabilityServiceWriter, *das.LifecycleManager, []daprovider.Reader, error) {
 	var daWriter das.DataAvailabilityServiceWriter
 	var daReader das.DataAvailabilityServiceReader
 	var dasLifecycleManager *das.LifecycleManager
 	var dasKeysetFetcher *das.KeysetFetcher
 	if config.DataAvailability.Enable {
+		var err error
 		if config.BatchPoster.Enable {
 			daWriter, daReader, dasKeysetFetcher, dasLifecycleManager, err = das.CreateBatchPosterDAS(ctx, &config.DataAvailability, dataSigner, l1client, deployInfo.SequencerInbox)
 			if err != nil {
-				return nil, err
+				return nil, nil, nil, err
 			}
 		} else {
 			daReader, dasKeysetFetcher, dasLifecycleManager, err = das.CreateDAReaderForNode(ctx, &config.DataAvailability, l1Reader, &deployInfo.SequencerInbox)
 			if err != nil {
-				return nil, err
+				return nil, nil, nil, err
 			}
 		}
 
@@ -602,12 +609,12 @@ func createNodeImpl(
 			daReader = das.NewReaderPanicWrapper(daReader)
 		}
 	} else if l2Config.ArbitrumChainParams.DataAvailabilityCommittee {
-		return nil, errors.New("a data availability service is required for this chain, but it was not configured")
+		return nil, nil, nil, errors.New("a data availability service is required for this chain, but it was not configured")
 	}
 
 	// We support a nil txStreamer for the pruning code
 	if txStreamer != nil && txStreamer.chainConfig.ArbitrumChainParams.DataAvailabilityCommittee && daReader == nil {
-		return nil, errors.New("data availability service required but unconfigured")
+		return nil, nil, nil, errors.New("data availability service required but unconfigured")
 	}
 	var dapReaders []daprovider.Reader
 	if daReader != nil {
@@ -616,16 +623,38 @@ func createNodeImpl(
 	if blobReader != nil {
 		dapReaders = append(dapReaders, daprovider.NewReaderForBlobReader(blobReader))
 	}
+
+	return daWriter, dasLifecycleManager, dapReaders, nil
+}
+
+func getInboxTrackerAndReader(
+	ctx context.Context,
+	arbDb ethdb.Database,
+	txStreamer *TransactionStreamer,
+	dapReaders []daprovider.Reader,
+	config *Config,
+	configFetcher ConfigFetcher,
+	l1client *ethclient.Client,
+	l1Reader *headerreader.HeaderReader,
+	deployInfo *chaininfo.RollupAddresses,
+	delayedBridge *DelayedBridge,
+	sequencerInbox *SequencerInbox,
+	exec execution.ExecutionSequencer,
+) (*InboxTracker, *InboxReader, error) {
 	inboxTracker, err := NewInboxTracker(arbDb, txStreamer, dapReaders, config.SnapSyncTest)
 	if err != nil {
-		return nil, err
+		return nil, nil, err
 	}
 	firstMessageBlock := new(big.Int).SetUint64(deployInfo.DeployedAt)
 	if config.SnapSyncTest.Enabled {
+		if exec == nil {
+			return nil, nil, errors.New("snap sync test requires an execution sequencer")
+		}
+
 		batchCount := config.SnapSyncTest.BatchCount
 		delayedMessageNumber, err := exec.NextDelayedMessageNumber()
 		if err != nil {
-			return nil, err
+			return nil, nil, err
 		}
 		if batchCount > delayedMessageNumber {
 			batchCount = delayedMessageNumber
@@ -638,39 +667,28 @@ func createNodeImpl(
 		}
 		block, err := FindBlockContainingBatchCount(ctx, deployInfo.Bridge, l1client, config.SnapSyncTest.ParentChainAssertionBlock, batchCount)
 		if err != nil {
-			return nil, err
+			return nil, nil, err
 		}
 		firstMessageBlock.SetUint64(block)
 	}
 	inboxReader, err := NewInboxReader(inboxTracker, l1client, l1Reader, firstMessageBlock, delayedBridge, sequencerInbox, func() *InboxReaderConfig { return &configFetcher.Get().InboxReader })
 	if err != nil {
-		return nil, err
+		return nil, nil, err
 	}
 	txStreamer.SetInboxReaders(inboxReader, delayedBridge)
 
-	var statelessBlockValidator *staker.StatelessBlockValidator
-	if config.BlockValidator.RedisValidationClientConfig.Enabled() || config.BlockValidator.ValidationServerConfigs[0].URL != "" {
-		statelessBlockValidator, err = staker.NewStatelessBlockValidator(
-			inboxReader,
-			inboxTracker,
-			txStreamer,
-			exec,
-			rawdb.NewTable(arbDb, storage.BlockValidatorPrefix),
-			dapReaders,
-			func() *staker.BlockValidatorConfig { return &configFetcher.Get().BlockValidator },
-			stack,
-		)
-	} else {
-		err = errors.New("no validator url specified")
-	}
-	if err != nil {
-		if config.ValidatorRequired() || config.Staker.Enable {
-			return nil, fmt.Errorf("%w: failed to init block validator", err)
-		}
-		log.Warn("validation not supported", "err", err)
-		statelessBlockValidator = nil
-	}
+	return inboxTracker, inboxReader, nil
+}
 
+func getBlockValidator(
+	config *Config,
+	configFetcher ConfigFetcher,
+	statelessBlockValidator *staker.StatelessBlockValidator,
+	inboxTracker *InboxTracker,
+	txStreamer *TransactionStreamer,
+	fatalErrChan chan error,
+) (*staker.BlockValidator, error) {
+	var err error
 	var blockValidator *staker.BlockValidator
 	if config.ValidatorRequired() {
 		blockValidator, err = staker.NewBlockValidator(
@@ -684,7 +702,27 @@ func createNodeImpl(
 			return nil, err
 		}
 	}
+	return blockValidator, err
+}
 
+func getStaker(
+	ctx context.Context,
+	config *Config,
+	configFetcher ConfigFetcher,
+	arbDb ethdb.Database,
+	l1Reader *headerreader.HeaderReader,
+	txOptsValidator *bind.TransactOpts,
+	syncMonitor *SyncMonitor,
+	parentChainID *big.Int,
+	l1client *ethclient.Client,
+	deployInfo *chaininfo.RollupAddresses,
+	txStreamer *TransactionStreamer,
+	inboxTracker *InboxTracker,
+	stack *node.Node,
+	fatalErrChan chan error,
+	statelessBlockValidator *staker.StatelessBlockValidator,
+	blockValidator *staker.BlockValidator,
+) (*multiprotocolstaker.MultiProtocolStaker, *MessagePruner, common.Address, error) {
 	var stakerObj *multiprotocolstaker.MultiProtocolStaker
 	var messagePruner *MessagePruner
 	var stakerAddr common.Address
@@ -700,7 +738,7 @@ func createNodeImpl(
 			parentChainID,
 		)
 		if err != nil {
-			return nil, err
+			return nil, nil, common.Address{}, err
 		}
 		getExtraGas := func() uint64 { return configFetcher.Get().Staker.ExtraGas }
 		// TODO: factor this out into separate helper, and split rest of node
@@ -712,23 +750,23 @@ func createNodeImpl(
 				if len(config.Staker.ContractWalletAddress) > 0 {
 					if !common.IsHexAddress(config.Staker.ContractWalletAddress) {
 						log.Error("invalid validator smart contract wallet", "addr", config.Staker.ContractWalletAddress)
-						return nil, errors.New("invalid validator smart contract wallet address")
+						return nil, nil, common.Address{}, errors.New("invalid validator smart contract wallet address")
 					}
 					tmpAddress := common.HexToAddress(config.Staker.ContractWalletAddress)
 					existingWalletAddress = &tmpAddress
 				}
 				// #nosec G115
 				wallet, err = validatorwallet.NewContract(dp, existingWalletAddress, deployInfo.ValidatorWalletCreator, deployInfo.Rollup, l1Reader, txOptsValidator, int64(deployInfo.DeployedAt), func(common.Address) {}, getExtraGas)
 				if err != nil {
-					return nil, err
+					return nil, nil, common.Address{}, err
 				}
 			} else {
 				if len(config.Staker.ContractWalletAddress) > 0 {
-					return nil, errors.New("validator contract wallet specified but flag to use a smart contract wallet was not specified")
+					return nil, nil, common.Address{}, errors.New("validator contract wallet specified but flag to use a smart contract wallet was not specified")
 				}
 				wallet, err = validatorwallet.NewEOA(dp, deployInfo.Rollup, l1client, getExtraGas)
 				if err != nil {
-					return nil, err
+					return nil, nil, common.Address{}, err
 				}
 			}
 		}
@@ -741,26 +779,134 @@ func createNodeImpl(
 
 		stakerObj, err = multiprotocolstaker.NewMultiProtocolStaker(stack, l1Reader, wallet, bind.CallOpts{}, func() *legacystaker.L1ValidatorConfig { return &configFetcher.Get().Staker }, &configFetcher.Get().Bold, blockValidator, statelessBlockValidator, nil, deployInfo.StakeToken, confirmedNotifiers, deployInfo.ValidatorUtils, deployInfo.Bridge, fatalErrChan)
 		if err != nil {
-			return nil, err
+			return nil, nil, common.Address{}, err
 		}
 		if err := wallet.Initialize(ctx); err != nil {
-			return nil, err
+			return nil, nil, common.Address{}, err
 		}
 		if dp != nil {
 			stakerAddr = dp.Sender()
 		}
 	}
 
+	return stakerObj, messagePruner, stakerAddr, nil
+}
+
+func getTransactionStreamer(
+	ctx context.Context,
+	arbDb ethdb.Database,
+	l2Config *params.ChainConfig,
+	exec execution.ExecutionClient,
+	broadcastServer *broadcaster.Broadcaster,
+	configFetcher ConfigFetcher,
+	fatalErrChan chan error,
+) (*TransactionStreamer, error) {
+	transactionStreamerConfigFetcher := func() *TransactionStreamerConfig { return &configFetcher.Get().TransactionStreamer }
+	txStreamer, err := NewTransactionStreamer(ctx, arbDb, l2Config, exec, broadcastServer, fatalErrChan, transactionStreamerConfigFetcher, &configFetcher.Get().SnapSyncTest)
+	if err != nil {
+		return nil, err
+	}
+	return txStreamer, nil
+}
+
+func getSeqCoordinator(
+	config *Config,
+	dataSigner signature.DataSignerFunc,
+	bpVerifier *contracts.AddressVerifier,
+	txStreamer *TransactionStreamer,
+	syncMonitor *SyncMonitor,
+	exec execution.ExecutionSequencer,
+) (*SeqCoordinator, error) {
+	var coordinator *SeqCoordinator
+	if config.SeqCoordinator.Enable {
+		if exec == nil {
+			return nil, errors.New("sequencer coordinator requires an execution sequencer")
+		}
+
+		var err error
+		coordinator, err = NewSeqCoordinator(dataSigner, bpVerifier, txStreamer, exec, syncMonitor, config.SeqCoordinator)
+		if err != nil {
+			return nil, err
+		}
+	} else if config.Sequencer && !config.Dangerous.NoSequencerCoordinator {
+		return nil, errors.New("sequencer must be enabled with coordinator, unless dangerous.no-sequencer-coordinator set")
+	}
+	return coordinator, nil
+}
+
+func getStatelessBlockValidator(
+	config *Config,
+	configFetcher ConfigFetcher,
+	inboxReader *InboxReader,
+	inboxTracker *InboxTracker,
+	txStreamer *TransactionStreamer,
+	exec execution.ExecutionRecorder,
+	arbDb ethdb.Database,
+	dapReaders []daprovider.Reader,
+	stack *node.Node,
+) (*staker.StatelessBlockValidator, error) {
+	var err error
+	var statelessBlockValidator *staker.StatelessBlockValidator
+	if config.BlockValidator.RedisValidationClientConfig.Enabled() || config.BlockValidator.ValidationServerConfigs[0].URL != "" {
+		if exec == nil {
+			return nil, errors.New("stateless block validator requires an execution recorder")
+		}
+
+		statelessBlockValidator, err = staker.NewStatelessBlockValidator(
+			inboxReader,
+			inboxTracker,
+			txStreamer,
+			exec,
+			rawdb.NewTable(arbDb, storage.BlockValidatorPrefix),
+			dapReaders,
+			func() *staker.BlockValidatorConfig { return &configFetcher.Get().BlockValidator },
+			stack,
+		)
+	} else {
+		err = errors.New("no validator url specified")
+	}
+	if err != nil {
+		if config.ValidatorRequired() || config.Staker.Enable {
+			return nil, fmt.Errorf("%w: failed to init block validator", err)
+		}
+		log.Warn("validation not supported", "err", err)
+		statelessBlockValidator = nil
+	}
+
+	return statelessBlockValidator, nil
+}
+
+func getBatchPoster(
+	ctx context.Context,
+	config *Config,
+	configFetcher ConfigFetcher,
+	txOptsBatchPoster *bind.TransactOpts,
+	daWriter das.DataAvailabilityServiceWriter,
+	l1Reader *headerreader.HeaderReader,
+	inboxTracker *InboxTracker,
+	txStreamer *TransactionStreamer,
+	exec execution.ExecutionBatchPoster,
+	arbDb ethdb.Database,
+	syncMonitor *SyncMonitor,
+	deployInfo *chaininfo.RollupAddresses,
+	parentChainID *big.Int,
+	dapReaders []daprovider.Reader,
+	stakerAddr common.Address,
+) (*BatchPoster, error) {
 	var batchPoster *BatchPoster
-	var delayedSequencer *DelayedSequencer
 	if config.BatchPoster.Enable {
+		if exec == nil {
+			return nil, errors.New("batch poster requires an execution batch poster")
+		}
+
 		if txOptsBatchPoster == nil && config.BatchPoster.DataPoster.ExternalSigner.URL == "" {
 			return nil, errors.New("batchposter, but no TxOpts")
 		}
 		var dapWriter daprovider.Writer
 		if daWriter != nil {
 			dapWriter = daprovider.NewWriterForDAS(daWriter)
 		}
+		var err error
 		batchPoster, err = NewBatchPoster(ctx, &BatchPosterOpts{
 			DataPosterDB:  rawdb.NewTable(arbDb, storage.BatchPosterPrefix),
 			L1Reader:      l1Reader,
@@ -785,21 +931,198 @@ func createNodeImpl(
 		}
 	}
 
-	// always create DelayedSequencer, it won't do anything if it is disabled
-	delayedSequencer, err = NewDelayedSequencer(l1Reader, inboxReader, exec, coordinator, func() *DelayedSequencerConfig { return &configFetcher.Get().DelayedSequencer })
+	return batchPoster, nil
+}
+
+func getDelayedSequencer(
+	l1Reader *headerreader.HeaderReader,
+	inboxReader *InboxReader,
+	exec execution.ExecutionSequencer,
+	configFetcher ConfigFetcher,
+	coordinator *SeqCoordinator,
+) (*DelayedSequencer, error) {
+	if exec == nil {
+		return nil, nil
+	}
+
+	// always create DelayedSequencer if exec is non nil, it won't do anything if it is disabled
+	delayedSequencer, err := NewDelayedSequencer(l1Reader, inboxReader, exec, coordinator, func() *DelayedSequencerConfig { return &configFetcher.Get().DelayedSequencer })
+	if err != nil {
+		return nil, err
+	}
+	return delayedSequencer, nil
+}
+
+func getNodeParentChainReaderDisabled(
+	ctx context.Context,
+	arbDb ethdb.Database,
+	stack *node.Node,
+	executionClient execution.ExecutionClient,
+	executionSequencer execution.ExecutionSequencer,
+	executionRecorder execution.ExecutionRecorder,
+	txStreamer *TransactionStreamer,
+	blobReader daprovider.BlobReader,
+	broadcastServer *broadcaster.Broadcaster,
+	broadcastClients *broadcastclients.BroadcastClients,
+	coordinator *SeqCoordinator,
+	maintenanceRunner *MaintenanceRunner,
+	syncMonitor *SyncMonitor,
+	configFetcher ConfigFetcher,
+	blockMetadataFetcher *BlockMetadataFetcher,
+) *Node {
+	return &Node{
+		ArbDB:                   arbDb,
+		Stack:                   stack,
+		ExecutionClient:         executionClient,
+		ExecutionSequencer:      executionSequencer,
+		ExecutionRecorder:       executionRecorder,
+		L1Reader:                nil,
+		TxStreamer:              txStreamer,
+		DeployInfo:              nil,
+		BlobReader:              blobReader,
+		InboxReader:             nil,
+		InboxTracker:            nil,
+		DelayedSequencer:        nil,
+		BatchPoster:             nil,
+		MessagePruner:           nil,
+		BlockValidator:          nil,
+		StatelessBlockValidator: nil,
+		Staker:                  nil,
+		BroadcastServer:         broadcastServer,
+		BroadcastClients:        broadcastClients,
+		SeqCoordinator:          coordinator,
+		MaintenanceRunner:       maintenanceRunner,
+		DASLifecycleManager:     nil,
+		SyncMonitor:             syncMonitor,
+		configFetcher:           configFetcher,
+		ctx:                     ctx,
+		blockMetadataFetcher:    blockMetadataFetcher,
+	}
+}
+
+func createNodeImpl(
+	ctx context.Context,
+	stack *node.Node,
+	executionClient execution.ExecutionClient,
+	executionSequencer execution.ExecutionSequencer,
+	executionRecorder execution.ExecutionRecorder,
+	executionBatchPoster execution.ExecutionBatchPoster,
+	arbDb ethdb.Database,
+	configFetcher ConfigFetcher,
+	l2Config *params.ChainConfig,
+	l1client *ethclient.Client,
+	deployInfo *chaininfo.RollupAddresses,
+	txOptsValidator *bind.TransactOpts,
+	txOptsBatchPoster *bind.TransactOpts,
+	dataSigner signature.DataSignerFunc,
+	fatalErrChan chan error,
+	parentChainID *big.Int,
+	blobReader daprovider.BlobReader,
+) (*Node, error) {
+	config := configFetcher.Get()
+
+	err := checkArbDbSchemaVersion(arbDb)
+	if err != nil {
+		return nil, err
+	}
+
+	syncMonitor := getSyncMonitor(configFetcher)
+
+	l1Reader, err := getL1Reader(ctx, config, configFetcher, l1client)
+	if err != nil {
+		return nil, err
+	}
+
+	broadcastServer, err := getBroadcastServer(config, configFetcher, dataSigner, l2Config.ChainID.Uint64(), fatalErrChan)
+	if err != nil {
+		return nil, err
+	}
+
+	txStreamer, err := getTransactionStreamer(ctx, arbDb, l2Config, executionClient, broadcastServer, configFetcher, fatalErrChan)
+	if err != nil {
+		return nil, err
+	}
+
+	bpVerifier, err := getBPVerifier(deployInfo, l1client)
+	if err != nil {
+		return nil, err
+	}
+
+	coordinator, err := getSeqCoordinator(config, dataSigner, bpVerifier, txStreamer, syncMonitor, executionSequencer)
+	if err != nil {
+		return nil, err
+	}
+
+	maintenanceRunner, err := getMaintenanceRunner(arbDb, configFetcher, coordinator, executionClient)
+	if err != nil {
+		return nil, err
+	}
+
+	broadcastClients, err := getBroadcastClients(config, configFetcher, txStreamer, l2Config.ChainID.Uint64(), bpVerifier, fatalErrChan)
+	if err != nil {
+		return nil, err
+	}
+
+	blockMetadataFetcher, err := getBlockMetadataFetcher(ctx, configFetcher, arbDb, executionClient)
+	if err != nil {
+		return nil, err
+	}
+
+	if !config.ParentChainReader.Enable {
+		return getNodeParentChainReaderDisabled(ctx, arbDb, stack, executionClient, executionSequencer, executionRecorder, txStreamer, blobReader, broadcastServer, broadcastClients, coordinator, maintenanceRunner, syncMonitor, configFetcher, blockMetadataFetcher), nil
+	}
+
+	delayedBridge, sequencerInbox, err := getDelayedBridgeAndSequencerInbox(deployInfo, l1client)
+	if err != nil {
+		return nil, err
+	}
+
+	daWriter, dasLifecycleManager, dapReaders, err := getDAS(ctx, config, l2Config, txStreamer, blobReader, l1Reader, deployInfo, dataSigner, l1client)
+	if err != nil {
+		return nil, err
+	}
+
+	inboxTracker, inboxReader, err := getInboxTrackerAndReader(ctx, arbDb, txStreamer, dapReaders, config, configFetcher, l1client, l1Reader, deployInfo, delayedBridge, sequencerInbox, executionSequencer)
+	if err != nil {
+		return nil, err
+	}
+
+	statelessBlockValidator, err := getStatelessBlockValidator(config, configFetcher, inboxReader, inboxTracker, txStreamer, executionRecorder, arbDb, dapReaders, stack)
+	if err != nil {
+		return nil, err
+	}
+
+	blockValidator, err := getBlockValidator(config, configFetcher, statelessBlockValidator, inboxTracker, txStreamer, fatalErrChan)
+	if err != nil {
+		return nil, err
+	}
+
+	stakerObj, messagePruner, stakerAddr, err := getStaker(ctx, config, configFetcher, arbDb, l1Reader, txOptsValidator, syncMonitor, parentChainID, l1client, deployInfo, txStreamer, inboxTracker, stack, fatalErrChan, statelessBlockValidator, blockValidator)
+	if err != nil {
+		return nil, err
+	}
+
+	batchPoster, err := getBatchPoster(ctx, config, configFetcher, txOptsBatchPoster, daWriter, l1Reader, inboxTracker, txStreamer, executionBatchPoster, arbDb, syncMonitor, deployInfo, parentChainID, dapReaders, stakerAddr)
+	if err != nil {
+		return nil, err
+	}
+
+	delayedSequencer, err := getDelayedSequencer(l1Reader, inboxReader, executionSequencer, configFetcher, coordinator)
 	if err != nil {
 		return nil, err
 	}
 
 	consensusExecutionSyncerConfigFetcher := func() *ConsensusExecutionSyncerConfig {
 		return &configFetcher.Get().ConsensusExecutionSyncer
 	}
-	consensusExecutionSyncer := NewConsensusExecutionSyncer(consensusExecutionSyncerConfigFetcher, inboxReader, exec, blockValidator)
+	consensusExecutionSyncer := NewConsensusExecutionSyncer(consensusExecutionSyncerConfigFetcher, inboxReader, executionClient, blockValidator)
 
 	return &Node{
 		ArbDB:                    arbDb,
 		Stack:                    stack,
-		Execution:                exec,
+		ExecutionClient:          executionClient,
+		ExecutionSequencer:       executionSequencer,
+		ExecutionRecorder:        executionRecorder,
 		L1Reader:                 l1Reader,
 		TxStreamer:               txStreamer,
 		DeployInfo:               deployInfo,
@@ -877,26 +1200,7 @@ func (n *Node) OnConfigReload(_ *Config, _ *Config) error {
 	return nil
 }
 
-func CreateNode(
-	ctx context.Context,
-	stack *node.Node,
-	exec execution.FullExecutionClient,
-	arbDb ethdb.Database,
-	configFetcher ConfigFetcher,
-	l2Config *params.ChainConfig,
-	l1client *ethclient.Client,
-	deployInfo *chaininfo.RollupAddresses,
-	txOptsValidator *bind.TransactOpts,
-	txOptsBatchPoster *bind.TransactOpts,
-	dataSigner signature.DataSignerFunc,
-	fatalErrChan chan error,
-	parentChainID *big.Int,
-	blobReader daprovider.BlobReader,
-) (*Node, error) {
-	currentNode, err := createNodeImpl(ctx, stack, exec, arbDb, configFetcher, l2Config, l1client, deployInfo, txOptsValidator, txOptsBatchPoster, dataSigner, fatalErrChan, parentChainID, blobReader)
-	if err != nil {
-		return nil, err
-	}
+func registerAPIs(currentNode *Node, stack *node.Node) {
 	var apis []rpc.API
 	if currentNode.BlockValidator != nil {
 		apis = append(apis, rpc.API{
@@ -927,12 +1231,67 @@ func CreateNode(
 		})
 	}
 	stack.RegisterAPIs(apis)
+}
 
+func CreateNodeExecutionClient(
+	ctx context.Context,
+	stack *node.Node,
+	executionClient execution.ExecutionClient,
+	arbDb ethdb.Database,
+	configFetcher ConfigFetcher,
+	l2Config *params.ChainConfig,
+	l1client *ethclient.Client,
+	deployInfo *chaininfo.RollupAddresses,
+	txOptsValidator *bind.TransactOpts,
+	txOptsBatchPoster *bind.TransactOpts,
+	dataSigner signature.DataSignerFunc,
+	fatalErrChan chan error,
+	parentChainID *big.Int,
+	blobReader daprovider.BlobReader,
+) (*Node, error) {
+	if executionClient == nil {
+		return nil, errors.New("execution client must be non-nil")
+	}
+	currentNode, err := createNodeImpl(ctx, stack, executionClient, nil, nil, nil, arbDb, configFetcher, l2Config, l1client, deployInfo, txOptsValidator, txOptsBatchPoster, dataSigner, fatalErrChan, parentChainID, blobReader)
+	if err != nil {
+		return nil, err
+	}
+	registerAPIs(currentNode, stack)
+	return currentNode, nil
+}
+
+func CreateNodeFullExecutionClient(
+	ctx context.Context,
+	stack *node.Node,
+	executionClient execution.ExecutionClient,
+	executionSequencer execution.ExecutionSequencer,
+	executionRecorder execution.ExecutionRecorder,
+	executionBatchPoster execution.ExecutionBatchPoster,
+	arbDb ethdb.Database,
+	configFetcher ConfigFetcher,
+	l2Config *params.ChainConfig,
+	l1client *ethclient.Client,
+	deployInfo *chaininfo.RollupAddresses,
+	txOptsValidator *bind.TransactOpts,
+	txOptsBatchPoster *bind.TransactOpts,
+	dataSigner signature.DataSignerFunc,
+	fatalErrChan chan error,
+	parentChainID *big.Int,
+	blobReader daprovider.BlobReader,
+) (*Node, error) {
+	if (executionClient == nil) || (executionSequencer == nil) || (executionRecorder == nil) || (executionBatchPoster == nil) {
+		return nil, errors.New("execution client, sequencer, recorder, and batch poster must be non-nil")
+	}
+	currentNode, err := createNodeImpl(ctx, stack, executionClient, executionSequencer, executionRecorder, executionBatchPoster, arbDb, configFetcher, l2Config, l1client, deployInfo, txOptsValidator, txOptsBatchPoster, dataSigner, fatalErrChan, parentChainID, blobReader)
+	if err != nil {
+		return nil, err
+	}
+	registerAPIs(currentNode, stack)
 	return currentNode, nil
 }
 
 func (n *Node) Start(ctx context.Context) error {
-	execClient, ok := n.Execution.(*gethexec.ExecutionNode)
+	execClient, ok := n.ExecutionClient.(*gethexec.ExecutionNode)
 	if !ok {
 		execClient = nil
 	}
@@ -950,7 +1309,7 @@ func (n *Node) Start(ctx context.Context) error {
 	if execClient != nil {
 		execClient.SetConsensusClient(n)
 	}
-	err = n.Execution.Start(ctx)
+	_, err = n.ExecutionClient.Start(ctx).Await(ctx)
 	if err != nil {
 		return fmt.Errorf("error starting exec client: %w", err)
 	}
@@ -999,8 +1358,8 @@ func (n *Node) Start(ctx context.Context) error {
 	}
 	if n.SeqCoordinator != nil {
 		n.SeqCoordinator.Start(ctx)
-	} else {
-		n.Execution.Activate()
+	} else if n.ExecutionSequencer != nil {
+		n.ExecutionSequencer.Activate()
 	}
 	if n.MaintenanceRunner != nil {
 		n.MaintenanceRunner.Start(ctx)
@@ -1126,8 +1485,11 @@ func (n *Node) StopAndWait() {
 	if n.DASLifecycleManager != nil {
 		n.DASLifecycleManager.StopAndWaitUntil(2 * time.Second)
 	}
-	if n.Execution != nil {
-		n.Execution.StopAndWait()
+	if n.ExecutionClient != nil {
+		_, err := n.ExecutionClient.StopAndWait().Await(n.ctx)
+		if err != nil {
+			log.Error("error stopping execution client", "err", err)
+		}
 	}
 	if err := n.Stack.Close(); err != nil {
 		log.Error("error on stack close", "err", err)
```

### arbnode/transaction_streamer.go
```diff
@@ -44,7 +44,7 @@ type TransactionStreamer struct {
 	stopwaiter.StopWaiter
 
 	chainConfig      *params.ChainConfig
-	exec             execution.ExecutionSequencer
+	exec             execution.ExecutionClient
 	execLastMsgCount arbutil.MessageIndex
 	validator        *staker.BlockValidator
 
@@ -102,9 +102,10 @@ func TransactionStreamerConfigAddOptions(prefix string, f *flag.FlagSet) {
 }
 
 func NewTransactionStreamer(
+	ctx context.Context,
 	db ethdb.Database,
 	chainConfig *params.ChainConfig,
-	exec execution.ExecutionSequencer,
+	exec execution.ExecutionClient,
 	broadcastServer *broadcaster.Broadcaster,
 	fatalErrChan chan<- error,
 	config TransactionStreamerConfigFetcher,
@@ -125,7 +126,7 @@ func NewTransactionStreamer(
 		return nil, err
 	}
 	if config().TrackBlockMetadataFrom != 0 {
-		trackBlockMetadataFrom, err := exec.BlockNumberToMessageIndex(config().TrackBlockMetadataFrom)
+		trackBlockMetadataFrom, err := exec.BlockNumberToMessageIndex(config().TrackBlockMetadataFrom).Await(ctx)
 		if err != nil {
 			return nil, err
 		}
@@ -366,7 +367,7 @@ func (s *TransactionStreamer) reorg(batch ethdb.Batch, count arbutil.MessageInde
 	s.reorgMutex.Lock()
 	defer s.reorgMutex.Unlock()
 
-	messagesResults, err := s.exec.Reorg(count, newMessages, oldMessages)
+	messagesResults, err := s.exec.Reorg(count, newMessages, oldMessages).Await(s.GetContext())
 	if err != nil {
 		return err
 	}
@@ -524,7 +525,7 @@ func (s *TransactionStreamer) GetProcessedMessageCount() (arbutil.MessageIndex,
 	if err != nil {
 		return 0, err
 	}
-	digestedHead, err := s.exec.HeadMessageNumber()
+	digestedHead, err := s.exec.HeadMessageNumber().Await(s.GetContext())
 	if err != nil {
 		return 0, err
 	}
@@ -710,7 +711,10 @@ func (s *TransactionStreamer) AddMessagesAndEndBatch(pos arbutil.MessageIndex, m
 
 	if messagesAreConfirmed {
 		// Trim confirmed messages from l1pricedataCache
-		s.exec.MarkFeedStart(pos + arbutil.MessageIndex(len(messages)))
+		_, err := s.exec.MarkFeedStart(pos + arbutil.MessageIndex(len(messages))).Await(s.GetContext())
+		if err != nil {
+			log.Warn("TransactionStreamer: failed to mark feed start", "pos", pos, "err", err)
+		}
 		s.reorgMutex.RLock()
 		dups, _, _, err := s.countDuplicateMessages(pos, messagesWithBlockInfo, nil)
 		s.reorgMutex.RUnlock()
@@ -1176,7 +1180,11 @@ func (s *TransactionStreamer) ResultAtCount(count arbutil.MessageIndex) (*execut
 	}
 	log.Info(FailedToGetMsgResultFromDB, "count", count)
 
-	msgResult, err := s.exec.ResultAtPos(pos)
+	ctx := context.Background()
+	if s.Started() {
+		ctx = s.GetContext()
+	}
+	msgResult, err := s.exec.ResultAtPos(pos).Await(ctx)
 	if err != nil {
 		return nil, err
 	}
@@ -1255,7 +1263,7 @@ func (s *TransactionStreamer) ExecuteNextMsg(ctx context.Context) bool {
 		return false
 	}
 	s.execLastMsgCount = msgCount
-	pos, err := s.exec.HeadMessageNumber()
+	pos, err := s.exec.HeadMessageNumber().Await(ctx)
 	if err != nil {
 		log.Error("feedOneMsg failed to get exec engine message count", "err", err)
 		return false
@@ -1278,7 +1286,7 @@ func (s *TransactionStreamer) ExecuteNextMsg(ctx context.Context) bool {
 		}
 		msgForPrefetch = msg
 	}
-	msgResult, err := s.exec.DigestMessage(pos, &msgAndBlockInfo.MessageWithMeta, msgForPrefetch)
+	msgResult, err := s.exec.DigestMessage(pos, &msgAndBlockInfo.MessageWithMeta, msgForPrefetch).Await(ctx)
 	if err != nil {
 		logger := log.Warn
 		if prevMessageCount < msgCount {
```

### arbos/arbosState/arbosstate.go
```diff
@@ -119,8 +119,8 @@ func NewArbosMemoryBackedArbOSState() (*ArbosState, *state.StateDB) {
 	if env.GetTestStateScheme() == rawdb.HashScheme {
 		trieConfig = &triedb.Config{Preimages: false, HashDB: hashdb.Defaults}
 	}
-	db := state.NewDatabaseWithConfig(raw, trieConfig)
-	statedb, err := state.New(common.Hash{}, db, nil)
+	db := state.NewDatabase(triedb.NewDatabase(raw, trieConfig), nil)
+	statedb, err := state.New(common.Hash{}, db)
 	if err != nil {
 		panic("failed to init empty statedb: " + err.Error())
 	}
```

### arbos/arbosState/initialization_test.go
```diff
@@ -13,6 +13,7 @@ import (
 	"github.com/ethereum/go-ethereum/core"
 	"github.com/ethereum/go-ethereum/core/rawdb"
 	"github.com/ethereum/go-ethereum/core/state"
+	"github.com/ethereum/go-ethereum/triedb"
 
 	"github.com/offchainlabs/nitro/arbos/arbostypes"
 	"github.com/offchainlabs/nitro/arbos/burn"
@@ -68,7 +69,7 @@ func tryMarshalUnmarshal(input *statetransfer.ArbosInitializationInfo, t *testin
 	stateroot, err := InitializeArbosInDatabase(raw, cacheConfig, initReader, chainConfig, arbostypes.TestInitMessage, 0, 0)
 	Require(t, err)
 	triedbConfig := cacheConfig.TriedbConfig()
-	stateDb, err := state.New(stateroot, state.NewDatabaseWithConfig(raw, triedbConfig), nil)
+	stateDb, err := state.New(stateroot, state.NewDatabase(triedb.NewDatabase(raw, triedbConfig), nil))
 	Require(t, err)
 
 	arbState, err := OpenArbosState(stateDb, &burn.SystemBurner{})
```

### arbos/arbosState/initialize.go
```diff
@@ -21,6 +21,7 @@ import (
 	"github.com/ethereum/go-ethereum/log"
 	"github.com/ethereum/go-ethereum/params"
 	"github.com/ethereum/go-ethereum/trie"
+	"github.com/ethereum/go-ethereum/triedb"
 
 	"github.com/offchainlabs/nitro/arbos/arbostypes"
 	"github.com/offchainlabs/nitro/arbos/burn"
@@ -60,11 +61,11 @@ func MakeGenesisBlock(parentHash common.Hash, blockNumber uint64, timestamp uint
 func InitializeArbosInDatabase(db ethdb.Database, cacheConfig *core.CacheConfig, initData statetransfer.InitDataReader, chainConfig *params.ChainConfig, initMessage *arbostypes.ParsedInitMessage, timestamp uint64, accountsPerSync uint) (root common.Hash, err error) {
 	triedbConfig := cacheConfig.TriedbConfig()
 	triedbConfig.Preimages = false
-	stateDatabase := state.NewDatabaseWithConfig(db, triedbConfig)
+	stateDatabase := state.NewDatabase(triedb.NewDatabase(db, triedbConfig), nil)
 	defer func() {
 		err = errors.Join(err, stateDatabase.TrieDB().Close())
 	}()
-	statedb, err := state.New(common.Hash{}, stateDatabase, nil)
+	statedb, err := state.New(common.Hash{}, stateDatabase)
 	if err != nil {
 		panic("failed to init empty statedb :" + err.Error())
 	}
@@ -86,7 +87,7 @@ func InitializeArbosInDatabase(db ethdb.Database, cacheConfig *core.CacheConfig,
 				return common.Hash{}, err
 			}
 		}
-		statedb, err = state.New(root, stateDatabase, nil)
+		statedb, err = state.New(root, stateDatabase)
 		if err != nil {
 			return common.Hash{}, err
 		}
```
