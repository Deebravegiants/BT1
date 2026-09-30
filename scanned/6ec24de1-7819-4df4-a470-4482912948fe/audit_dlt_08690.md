# [?] Merge branch 'master' into fix/stopwaiter-rlock-deadlock

## Summary
Severity: Unknown
Chain: Arbitrum
Component: OffchainLabs/nitro
Published: 2026-04-09
Source: https://github.com/OffchainLabs/nitro/commit/809f378e10fc44ed4334451c1fcb8dd4cff253cc
Type: security-commit

## Details
Merge branch 'master' into fix/stopwaiter-rlock-deadlock

## Patch
### .dockerignore
```diff
@@ -27,7 +27,7 @@ crates/tools/module_roots
 crates/tools/pricer
 
 # Rust outputs
-crates/stylus/tests/*/target/
+crates/stylus/tests/target/
 crates/wasm-testsuite/target/
 crates/wasm-libraries/target/
 crates/tools/wasmer/target/
```

### Dockerfile
```diff
@@ -301,6 +301,7 @@ COPY --from=node-builder  /workspace/target/bin/anytrusttool    /usr/local/bin/
 RUN ln -s /usr/local/bin/anytrusttool /usr/local/bin/datool
 COPY --from=node-builder  /workspace/target/bin/genesis-generator  /usr/local/bin/
 COPY --from=node-builder  /workspace/target/bin/transaction-filterer  /usr/local/bin/
+COPY --from=node-builder  /workspace/target/bin/filtering-report  /usr/local/bin/
 COPY --from=contracts-builder  /workspace/contracts/  /contracts/
 COPY --from=contracts-builder  /workspace/contracts-local/  /contracts-local/
 COPY --from=nitro-legacy /home/user/target/machines /home/user/nitro-legacy/machines
```

### Makefile
```diff
@@ -124,7 +124,7 @@ stylus_lang_rust = $(wildcard $(rust_sdk)/*/src/*.rs $(rust_sdk)/*/src/*/*.rs $(
 stylus_lang_c    = $(wildcard $(c_sdk)/*/*.c $(c_sdk)/*/*.h)
 stylus_lang_bf   = $(wildcard crates/langs/bf/src/*.* crates/langs/bf/src/*.toml)
 
-get_stylus_test_wasm = $(stylus_test_dir)/$(1)/$(wasm32_unknown)/$(1).wasm
+get_stylus_test_wasm = $(stylus_test_dir)/$(wasm32_unknown)/$(1).wasm
 get_stylus_test_rust = $(wildcard $(stylus_test_dir)/$(1)/*.toml $(stylus_test_dir)/$(1)/src/*.rs) $(stylus_cargo) $(stylus_lang_rust)
 get_stylus_test_c    = $(wildcard $(c_sdk)/examples/$(1)/*.c $(c_sdk)/examples/$(1)/*.h) $(stylus_lang_c)
 stylus_test_bfs      = $(wildcard $(stylus_test_dir)/bf/*.b)
@@ -173,7 +173,7 @@ all: build build-replay-env test-gen-proofs
 	@touch .make/all
 
 .PHONY: build
-build: $(patsubst %,$(output_root)/bin/%, nitro deploy relay daprovider anytrustserver autonomous-auctioneer bidder-client anytrusttool blobtool el-proxy mockexternalsigner seq-coordinator-invalidate nitro-val seq-coordinator-manager dbconv genesis-generator transaction-filterer)
+build: $(patsubst %,$(output_root)/bin/%, nitro deploy relay daprovider anytrustserver autonomous-auctioneer bidder-client anytrusttool blobtool el-proxy mockexternalsigner seq-coordinator-invalidate nitro-val seq-coordinator-manager dbconv genesis-generator transaction-filterer filtering-report)
 	@printf $(done)
 
 .PHONY: build-node-deps
@@ -293,7 +293,7 @@ clean:
 	rm -f crates/wasm-libraries/soft-float/SoftFloat/build/Wasm-Clang/*.o
 	rm -f crates/wasm-libraries/soft-float/SoftFloat/build/Wasm-Clang/*.a
 	rm -f crates/wasm-libraries/forward/*.wat
-	rm -rf crates/stylus/tests/*/target/ crates/stylus/tests/*/*.wasm
+	rm -rf crates/stylus/tests/target/ crates/stylus/tests/*/*.wasm
 	rm -rf brotli/buildfiles
 	@rm -rf contracts/build contracts/cache solgen/go/
 	@rm -rf contracts-legacy/build contracts-legacy/cache
@@ -363,6 +363,9 @@ $(output_root)/bin/dbconv: $(DEP_PREDICATE) build-node-deps
 $(output_root)/bin/transaction-filterer: $(DEP_PREDICATE) build-node-deps
 	go build $(GOLANG_PARAMS) -o $@ "$(CURDIR)/cmd/transaction-filterer"
 
+$(output_root)/bin/filtering-report: $(DEP_PREDICATE) build-node-deps
+	go build $(GOLANG_PARAMS) -o $@ "$(CURDIR)/cmd/filtering-report"
+
 # recompile wasm, but don't change timestamp unless files differ
 $(replay_wasm): $(DEP_PREDICATE) $(go_source) .make/solgen
 	mkdir -p `dirname $(replay_wasm)`
```

### arbnode/inbox_test.go
```diff
@@ -141,7 +141,7 @@ func NewTransactionStreamerForTest(t *testing.T, ctx context.Context, ownerAddre
 	}
 
 	transactionStreamerConfigFetcher := func() *TransactionStreamerConfig { return &DefaultTransactionStreamerConfig }
-	execEngine := gethexec.NewExecutionEngine(bc, 0, false, false)
+	execEngine := gethexec.NewExecutionEngine(bc, 0, false, false, nil)
 	stylusTargetConfig := &gethexec.DefaultStylusTargetConfig
 	Require(t, stylusTargetConfig.Validate()) // pre-processes config (i.a. parses wasmTargets)
 	if err := execEngine.Initialize(gethexec.DefaultCachingConfig.StylusLRUCacheCapacity, &gethexec.DefaultStylusTargetConfig); err != nil {
```

### arbnode/mel/runner/database.go
```diff
@@ -51,6 +51,7 @@ func (d *Database) setMelState(batch ethdb.KeyValueWriter, parentChainBlockNumbe
 	if err != nil {
 		return err
 	}
+	melStateSizeBytesGauge.Update(int64(len(melStateBytes)))
 	if err := batch.Put(key, melStateBytes); err != nil {
 		return err
 	}
```

### arbnode/mel/runner/mel.go
```diff
@@ -18,7 +18,6 @@ import (
 	"github.com/ethereum/go-ethereum/core/rawdb"
 	"github.com/ethereum/go-ethereum/core/types"
 	"github.com/ethereum/go-ethereum/log"
-	"github.com/ethereum/go-ethereum/metrics"
 	"github.com/ethereum/go-ethereum/params"
 	"github.com/ethereum/go-ethereum/rpc"
 
@@ -29,46 +28,49 @@ import (
 	"github.com/offchainlabs/nitro/bold/containers/fsm"
 	"github.com/offchainlabs/nitro/cmd/chaininfo"
 	"github.com/offchainlabs/nitro/daprovider"
+	"github.com/offchainlabs/nitro/staker"
 	"github.com/offchainlabs/nitro/util/headerreader"
 	"github.com/offchainlabs/nitro/util/stopwaiter"
 )
 
-var (
-	stuckFSMIndicatingGauge = metrics.NewRegisteredGauge("arb/mel/stuck", nil) // 1-stuck, 0-not_stuck
-)
-
 type MessageExtractionConfig struct {
-	Enable           bool          `koanf:"enable"`
-	RetryInterval    time.Duration `koanf:"retry-interval"`
-	BlocksToPrefetch uint64        `koanf:"blocks-to-prefetch"`
-	ReadMode         string        `koanf:"read-mode"`
-	StallTolerance   uint64        `koanf:"stall-tolerance"`
+	Enable                             bool          `koanf:"enable"`
+	RetryInterval                      time.Duration `koanf:"retry-interval"`
+	BlocksToPrefetch                   uint64        `koanf:"blocks-to-prefetch"`
+	ReadMode                           string        `koanf:"read-mode"`
+	StallTolerance                     uint64        `koanf:"stall-tolerance"`
+	LogExtractionStatusFrequencyBlocks uint64        `koanf:"log-extraction-status-frequency-blocks"`
 }
 
 func (c *MessageExtractionConfig) Validate() error {
 	c.ReadMode = strings.ToLower(c.ReadMode)
 	if c.ReadMode != "latest" && c.ReadMode != "safe" && c.ReadMode != "finalized" {
 		return fmt.Errorf("inbox reader read-mode is invalid, want: latest or safe or finalized, got: %s", c.ReadMode)
 	}
+	if c.LogExtractionStatusFrequencyBlocks == 0 {
+		return errors.New("log-extraction-status-frequency-blocks must be greater than 0")
+	}
 	return nil
 }
 
 var DefaultMessageExtractionConfig = MessageExtractionConfig{
 	Enable: false,
 	// The retry interval for the message extractor FSM. After each tick of the FSM,
 	// the extractor service stop waiter will wait for this duration before trying to act again.
-	RetryInterval:    time.Millisecond * 500,
-	BlocksToPrefetch: 499, // 500 is the eth_getLogs block range limit
-	ReadMode:         "latest",
-	StallTolerance:   10,
+	RetryInterval:                      time.Millisecond * 500,
+	BlocksToPrefetch:                   499, // 500 is the eth_getLogs block range limit
+	ReadMode:                           "latest",
+	StallTolerance:                     10,
+	LogExtractionStatusFrequencyBlocks: 100,
 }
 
 var TestMessageExtractionConfig = MessageExtractionConfig{
-	Enable:           false,
-	RetryInterval:    time.Millisecond * 10,
-	BlocksToPrefetch: 499,
-	ReadMode:         "latest",
-	StallTolerance:   10,
+	Enable:                             false,
+	RetryInterval:                      time.Millisecond * 10,
+	BlocksToPrefetch:                   499,
+	ReadMode:                           "latest",
+	StallTolerance:                     10,
+	LogExtractionStatusFrequencyBlocks: 100,
 }
 
 func MessageExtractionConfigAddOptions(prefix string, f *pflag.FlagSet) {
@@ -77,6 +79,7 @@ func MessageExtractionConfigAddOptions(prefix string, f *pflag.FlagSet) {
 	f.Uint64(prefix+".blocks-to-prefetch", DefaultMessageExtractionConfig.BlocksToPrefetch, "the number of blocks to prefetch relevant logs from. Recommend using max allowed range for eth_getLogs rpc query")
 	f.String(prefix+".read-mode", DefaultMessageExtractionConfig.ReadMode, "mode to only read latest or safe or finalized L1 blocks. Enabling safe or finalized disables feed input and output. Defaults to latest. Takes string input, valid strings- latest, safe, finalized")
 	f.Uint64(prefix+".stall-tolerance", DefaultMessageExtractionConfig.StallTolerance, "max times the MEL fsm is allowed to be stuck without logging error")
+	f.Uint64(prefix+".log-extraction-status-frequency-blocks", DefaultMessageExtractionConfig.LogExtractionStatusFrequencyBlocks, "frequency of logging message extraction status in terms of number of blocks processed")
 }
 
 // SequencerBatchCountFetcher queries the on-chain sequencer inbox batch count at a given parent chain block.
@@ -321,6 +324,17 @@ func (m *MessageExtractor) GetMsgCount() (arbutil.MessageIndex, error) {
 	return arbutil.MessageIndex(headState.MsgCount), nil
 }
 
+func (m *MessageExtractor) GetDelayedMessageBytes(ctx context.Context, seqNum uint64) ([]byte, error) {
+	msg, err := m.GetDelayedMessage(seqNum)
+	if err != nil {
+		return nil, err
+	}
+	if msg.Message == nil {
+		return nil, fmt.Errorf("message at seqNum %d has nil Message field", seqNum)
+	}
+	return msg.Message.Serialize()
+}
+
 func (m *MessageExtractor) GetDelayedMessage(index uint64) (*mel.DelayedInboxMessage, error) {
 	headState, err := m.melDB.GetHeadMelState()
 	if err != nil {
@@ -519,6 +533,10 @@ func (m *MessageExtractor) FindInboxBatchContainingMessage(pos arbutil.MessageIn
 	}
 }
 
+func (m *MessageExtractor) SetBlockValidator(_ *staker.BlockValidator) {
+	log.Info("MEL does not support block validation registration; SetBlockValidator is a no-op")
+}
+
 func (m *MessageExtractor) GetBatchCount() (uint64, error) {
 	headState, err := m.melDB.GetHeadMelState()
 	if err != nil {
@@ -527,6 +545,14 @@ func (m *MessageExtractor) GetBatchCount() (uint64, error) {
 	return headState.BatchCount, nil
 }
 
+func (m *MessageExtractor) GetBatchAcc(seqNum uint64) (common.Hash, error) {
+	metadata, err := m.GetBatchMetadata(seqNum)
+	if err != nil {
+		return common.Hash{}, err
+	}
+	return metadata.Accumulator, nil
+}
+
 func (m *MessageExtractor) CaughtUp() chan struct{} {
 	return m.caughtUpChan
 }
@@ -549,13 +575,15 @@ func (m *MessageExtractor) Act(ctx context.Context) (time.Duration, error) {
 	// from the parent chain block. The FSM will transition to the `SavingMessages`
 	// state after successfully extracting messages.
 	case ProcessingNextBlock:
+		fsmBlocksProcessedCounter.Inc(1)
 		return m.processNextBlock(ctx, current)
 	// `SavingMessages` is the state responsible for saving the extracted messages
 	// and delayed messages to the database. It stores data in the node's consensus database
 	// and runs after the `ProcessingNextBlock` state.
 	// After data is stored, the FSM will then transition to the `ProcessingNextBlock` state
 	// yet again.
 	case SavingMessages:
+		fsmSaveMessagesCounter.Inc(1)
 		return m.saveMessages(ctx, current)
 	// `Reorging` is the state responsible for handling reorgs in the parent chain.
 	// It is triggered when a reorg occurs, and it will revert the MEL state being processed to the
```

### arbnode/mel/runner/metrics.go
```diff
@@ -0,0 +1,32 @@
+package melrunner
+
+import "github.com/ethereum/go-ethereum/metrics"
+
+var (
+	// FSM health.
+	stuckFSMIndicatingGauge   = metrics.NewRegisteredGauge("arb/mel/stuck", nil) // 1-stuck, 0-not_stuck
+	fsmBlocksProcessedCounter = metrics.NewRegisteredCounter("arb/mel/fsm/process_block_total", nil)
+	fsmSaveMessagesCounter    = metrics.NewRegisteredCounter("arb/mel/fsm/save_messages_total", nil)
+
+	// State progress.
+	latestBlockGauge            = metrics.NewRegisteredGauge("arb/mel/latest/parent_chain_block_number", nil)
+	latestMsgCountGauge         = metrics.NewRegisteredGauge("arb/mel/latest/msg_count", nil)
+	latestDelayedSeenCountGauge = metrics.NewRegisteredGauge("arb/mel/latest/delayed_msg_seen_count", nil)
+	latestDelayedReadCountGauge = metrics.NewRegisteredGauge("arb/mel/latest/delayed_msg_read_count", nil)
+
+	// Throughput.
+	msgsExtractedCounter = metrics.NewRegisteredCounter("arb/mel/msgs/extracted_total", nil)
+	msgsPushedCounter    = metrics.NewRegisteredCounter("arb/mel/msgs/pushed_to_execution_total", nil)
+
+	// Errors.
+	extractionErrors = metrics.NewRegisteredCounter("arb/mel/errors/extraction_function_errors_total", nil)
+
+	// Reorgs
+	reorgCounter = metrics.NewRegisteredCounter("arb/mel/reorgs_total", nil)
+
+	// Performance.
+	blockProcessTimeGauge = metrics.NewRegisteredGauge("arb/mel/block_processing_time_micros", nil)
+
+	// MEL state size bytes.
+	melStateSizeBytesGauge = metrics.NewRegisteredGauge("arb/mel/mel_state_size_bytes", nil)
+)
```

### arbnode/mel/runner/process_next_block.go
```diff
@@ -15,7 +15,7 @@ import (
 	"github.com/ethereum/go-ethereum/rpc"
 
 	"github.com/offchainlabs/nitro/arbnode/mel"
-	"github.com/offchainlabs/nitro/arbnode/mel/extraction"
+	melextraction "github.com/offchainlabs/nitro/arbnode/mel/extraction"
 	"github.com/offchainlabs/nitro/bold/containers/fsm"
 )
 
@@ -81,6 +81,7 @@ func (m *MessageExtractor) processNextBlock(ctx context.Context, current *fsm.Cu
 	if err = m.logsAndHeadersPreFetcher.fetch(ctx, preState); err != nil {
 		return m.config.RetryInterval, err
 	}
+	start := time.Now()
 	postState, msgs, delayedMsgs, batchMetas, err := melextraction.ExtractMessages(
 		ctx,
 		preState,
@@ -92,6 +93,7 @@ func (m *MessageExtractor) processNextBlock(ctx context.Context, current *fsm.Cu
 		m.chainConfig,
 	)
 	if err != nil {
+		extractionErrors.Inc(1)
 		if errors.Is(err, mel.ErrDelayedMessagePreimageNotFound) {
 			if err := preState.RebuildDelayedMsgPreimages(m.melDB.FetchDelayedMessage); err != nil {
 				return m.config.RetryInterval, fmt.Errorf("error rebuilding delayed msg preimages when missing some preimages: %w", err)
@@ -100,6 +102,25 @@ func (m *MessageExtractor) processNextBlock(ctx context.Context, current *fsm.Cu
 		}
 		return m.config.RetryInterval, err
 	}
+	elapsed := time.Since(start)
+	// After processing every 100 parent chain blocks, print a status log
+	if postState.ParentChainBlockNumber%m.config.LogExtractionStatusFrequencyBlocks == 0 {
+		log.Info("Message extraction successful", "parentChainBlockNumber", postState.ParentChainBlockNumber, "msgCount", postState.MsgCount)
+	}
+
+	// Update metrics.
+	//#nosec G115
+	latestBlockGauge.Update(int64(postState.ParentChainBlockNumber))
+	//#nosec G115
+	latestMsgCountGauge.Update(int64(postState.MsgCount))
+	//#nosec G115
+	latestDelayedSeenCountGauge.Update(int64(postState.DelayedMessagesSeen))
+	//#nosec G115
+	latestDelayedReadCountGauge.Update(int64(postState.DelayedMessagesRead))
+	//#nosec G115
+	msgsExtractedCounter.Inc(int64(len(msgs)))
+	blockProcessTimeGauge.Update(elapsed.Microseconds())
+
 	// Begin the next FSM state immediately.
 	return 0, m.fsm.Do(saveMessages{
 		preStateMsgCount: preState.MsgCount,
```

### arbnode/mel/runner/reorg.go
```diff
@@ -25,6 +25,9 @@ func (m *MessageExtractor) reorg(ctx context.Context, current *fsm.CurrentState[
 		return m.config.RetryInterval, err
 	}
 	m.logsAndHeadersPreFetcher.reset()
+
+	// Update metrics.
+	reorgCounter.Inc(1)
 	return 0, m.fsm.Do(processNextBlock{
 		prevStepWasReorg: true,
 		melState:         previousState,
```

### arbnode/mel/runner/save_messages.go
```diff
@@ -31,6 +31,7 @@ func (m *MessageExtractor) saveMessages(ctx context.Context, current *fsm.Curren
 		log.Error("Error saving latest state as head state to db", "err", err)
 		return m.config.RetryInterval, err
 	}
+	msgsPushedCounter.Inc(int64(len(saveAction.messages)))
 	return 0, m.fsm.Do(processNextBlock{
 		melState: saveAction.postState,
 	})
```

### arbnode/node.go
```diff
@@ -756,6 +756,7 @@ func getInboxTrackerAndReader(
 	sequencerInbox *SequencerInbox,
 ) (*InboxTracker, *InboxReader, error) {
 	if config.MessageExtraction.Enable {
+		log.Info("Inbox reader and tracker disabled")
 		return nil, nil, nil
 	}
 	inboxTracker, err := NewInboxTracker(consensusDB, txStreamer, dapReaders)
@@ -863,6 +864,7 @@ func getMessageExtractor(
 	if err != nil {
 		return nil, err
 	}
+	log.Info("Message extractor enabled")
 	return msgExtractor, nil
 }
 
@@ -939,6 +941,7 @@ func getStaker(
 	statelessBlockValidator *staker.StatelessBlockValidator,
 	blockValidator *staker.BlockValidator,
 	dapRegistry *daprovider.DAProviderRegistry,
+	messageExtractor *melrunner.MessageExtractor,
 ) (*multiprotocolstaker.MultiProtocolStaker, *MessagePruner, common.Address, error) {
 	var stakerObj *multiprotocolstaker.MultiProtocolStaker
 	var messagePruner *MessagePruner
@@ -990,11 +993,26 @@ func getStaker(
 
 		var confirmedNotifiers []legacystaker.LatestConfirmedNotifier
 		if config.MessagePruner.Enable {
+			if inboxTracker == nil {
+				return nil, nil, common.Address{}, errors.New("message pruning cannot be enabled when inbox tracker is disabled (e.g. with Message Extraction enabled)")
+			}
 			messagePruner = NewMessagePruner(txStreamer, inboxTracker, func() *MessagePrunerConfig { return &configFetcher.Get().MessagePruner })
 			confirmedNotifiers = append(confirmedNotifiers, messagePruner)
 		}
 
-		stakerObj, err = multiprotocolstaker.NewMultiProtocolStaker(stack, l1Reader, wallet, bind.CallOpts{}, func() *legacystaker.L1ValidatorConfig { return &configFetcher.Get().Staker }, &configFetcher.Get().Bold, blockValidator, statelessBlockValidator, nil, deployInfo.StakeToken, deployInfo.Rollup, confirmedNotifiers, deployInfo.ValidatorUtils, deployInfo.Bridge, txStreamer, inboxTracker, inboxReader, dapRegistry, fatalErrChan)
+		var tracker staker.InboxTrackerInterface
+		var reader staker.InboxReaderInterface
+		if messageExtractor != nil {
+			tracker = messageExtractor
+			reader = messageExtractor
+		} else {
+			tracker = inboxTracker
+			reader = inboxReader
+		}
+		if tracker == nil || reader == nil {
+			return nil, nil, common.Address{}, errors.New("staker requires either message extractor or inbox tracker/reader")
+		}
+		stakerObj, err = multiprotocolstaker.NewMultiProtocolStaker(stack, l1Reader, wallet, bind.CallOpts{}, func() *legacystaker.L1ValidatorConfig { return &configFetcher.Get().Staker }, &configFetcher.Get().Bold, blockValidator, statelessBlockValidator, nil, deployInfo.StakeToken, deployInfo.Rollup, confirmedNotifiers, deployInfo.ValidatorUtils, deployInfo.Bridge, txStreamer, tracker, reader, dapRegistry, fatalErrChan)
 		if err != nil {
 			return nil, nil, common.Address{}, err
 		}
@@ -1363,7 +1381,7 @@ func createNodeImpl(
 		return nil, err
 	}
 
-	stakerObj, messagePruner, stakerAddr, err := getStaker(ctx, config, configFetcher, consensusDB, l1Reader, txOptsValidator, syncMonitor, parentChain, l1client, deployInfo, txStreamer, inboxTracker, inboxReader, stack, fatalErrChan, statelessBlockValidator, blockValidator, dapRegistry)
+	stakerObj, messagePruner, stakerAddr, err := getStaker(ctx, config, configFetcher, consensusDB, l1Reader, txOptsValidator, syncMonitor, parentChain, l1client, deployInfo, txStreamer, inboxTracker, inboxReader, stack, fatalErrChan, statelessBlockValidator, blockValidator, dapRegistry, messageExtractor)
 	if err != nil {
 		return nil, err
 	}
```

### arbnode/transaction_streamer.go
```diff
@@ -29,7 +29,7 @@ import (
 	"github.com/ethereum/go-ethereum/rlp"
 
 	"github.com/offchainlabs/nitro/arbnode/db/schema"
-	"github.com/offchainlabs/nitro/arbnode/mel/runner"
+	melrunner "github.com/offchainlabs/nitro/arbnode/mel/runner"
 	"github.com/offchainlabs/nitro/arbos/arbostypes"
 	"github.com/offchainlabs/nitro/arbutil"
 	"github.com/offchainlabs/nitro/broadcastclient"
```
