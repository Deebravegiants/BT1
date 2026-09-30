# [?] Merge branch 'advisory-fix' of https://github.com/multiversx/mx-chain-go-ghsa-pm7x-xvmm-jpfw into advisory-fix-1

## Summary
Severity: Unknown
Chain: MultiversX
Component: multiversx/mx-chain-go
Published: 2026-04-20
Source: https://github.com/multiversx/mx-chain-go/commit/c3f896562504d0269a71f7301dea1eba90c74bf7
Type: security-commit

## Details
Merge branch 'advisory-fix' of https://github.com/multiversx/mx-chain-go-ghsa-pm7x-xvmm-jpfw into advisory-fix-1

## Patch
### factory/processing/blockProcessorCreator.go
```diff
@@ -365,12 +365,12 @@ func (pcf *processComponentsFactory) newShardBlockProcessor(
 		return nil, err
 	}
 
-	argsDetector := coordinator.ArgsPrintDoubleTransactionsDetector{
+	argsDetector := coordinator.ArgsDoubleTransactionsDetector{
 		Marshaller:          pcf.coreData.InternalMarshalizer(),
 		Hasher:              pcf.coreData.Hasher(),
 		EnableEpochsHandler: pcf.coreData.EnableEpochsHandler(),
 	}
-	doubleTransactionsDetector, err := coordinator.NewPrintDoubleTransactionsDetector(argsDetector)
+	doubleTransactionsDetector, err := coordinator.NewDoubleTransactionsDetector(argsDetector)
 	if err != nil {
 		return nil, err
 	}
@@ -675,12 +675,12 @@ func (pcf *processComponentsFactory) newMetaBlockProcessor(
 		return nil, err
 	}
 
-	argsDetector := coordinator.ArgsPrintDoubleTransactionsDetector{
+	argsDetector := coordinator.ArgsDoubleTransactionsDetector{
 		Marshaller:          pcf.coreData.InternalMarshalizer(),
 		Hasher:              pcf.coreData.Hasher(),
 		EnableEpochsHandler: pcf.coreData.EnableEpochsHandler(),
 	}
-	doubleTransactionsDetector, err := coordinator.NewPrintDoubleTransactionsDetector(argsDetector)
+	doubleTransactionsDetector, err := coordinator.NewDoubleTransactionsDetector(argsDetector)
 	if err != nil {
 		return nil, err
 	}
```

### genesis/process/metaGenesisBlockCreator.go
```diff
@@ -525,12 +525,12 @@ func createProcessorsForMetaGenesisBlock(arg ArgsGenesisBlockCreator, enableEpoc
 		return nil, err
 	}
 
-	argsDetector := coordinator.ArgsPrintDoubleTransactionsDetector{
+	argsDetector := coordinator.ArgsDoubleTransactionsDetector{
 		Marshaller:          arg.Core.InternalMarshalizer(),
 		Hasher:              arg.Core.Hasher(),
 		EnableEpochsHandler: enableEpochsHandler,
 	}
-	doubleTransactionsDetector, err := coordinator.NewPrintDoubleTransactionsDetector(argsDetector)
+	doubleTransactionsDetector, err := coordinator.NewDoubleTransactionsDetector(argsDetector)
 	if err != nil {
 		return nil, err
 	}
```

### genesis/process/shardGenesisBlockCreator.go
```diff
@@ -615,12 +615,12 @@ func createProcessorsForShardGenesisBlock(arg ArgsGenesisBlockCreator, enableEpo
 		return nil, err
 	}
 
-	argsDetector := coordinator.ArgsPrintDoubleTransactionsDetector{
+	argsDetector := coordinator.ArgsDoubleTransactionsDetector{
 		Marshaller:          arg.Core.InternalMarshalizer(),
 		Hasher:              arg.Core.Hasher(),
 		EnableEpochsHandler: enableEpochsHandler,
 	}
-	doubleTransactionsDetector, err := coordinator.NewPrintDoubleTransactionsDetector(argsDetector)
+	doubleTransactionsDetector, err := coordinator.NewDoubleTransactionsDetector(argsDetector)
 	if err != nil {
 		return nil, err
 	}
```

### integrationTests/testProcessorNode.go
```diff
@@ -1857,7 +1857,7 @@ func (tpn *TestProcessorNode) initInnerProcessors(gasMap map[string]map[string]u
 		TransactionsLogProcessor:     tpn.TransactionLogProcessor,
 		EnableEpochsHandler:          tpn.EnableEpochsHandler,
 		ScheduledTxsExecutionHandler: scheduledTxsExecutionHandler,
-		DoubleTransactionsDetector:   &testscommon.PanicDoubleTransactionsDetector{},
+		DoubleTransactionsDetector:   &testscommon.DoubleTransactionsDetector{},
 		ProcessedMiniBlocksTracker:   processedMiniBlocksTracker,
 		TxExecutionOrderHandler:      tpn.TxExecutionOrderHandler,
 	}
@@ -2128,7 +2128,7 @@ func (tpn *TestProcessorNode) initMetaInnerProcessors(gasMap map[string]map[stri
 		TransactionsLogProcessor:     tpn.TransactionLogProcessor,
 		EnableEpochsHandler:          tpn.EnableEpochsHandler,
 		ScheduledTxsExecutionHandler: scheduledTxsExecutionHandler,
-		DoubleTransactionsDetector:   &testscommon.PanicDoubleTransactionsDetector{},
+		DoubleTransactionsDetector:   &testscommon.DoubleTransactionsDetector{},
 		ProcessedMiniBlocksTracker:   processedMiniBlocksTracker,
 		TxExecutionOrderHandler:      tpn.TxExecutionOrderHandler,
 	}
```

### process/block/baseProcess_test.go
```diff
@@ -468,7 +468,7 @@ func createMockTransactionCoordinatorArguments(
 		TransactionsLogProcessor:     &mock.TxLogsProcessorStub{},
 		EnableEpochsHandler:          enableEpochsHandlerMock.NewEnableEpochsHandlerStub(),
 		ScheduledTxsExecutionHandler: &testscommon.ScheduledTxsExecutionStub{},
-		DoubleTransactionsDetector:   &testscommon.PanicDoubleTransactionsDetector{},
+		DoubleTransactionsDetector:   &testscommon.DoubleTransactionsDetector{},
 		ProcessedMiniBlocksTracker:   &testscommon.ProcessedMiniBlocksTrackerStub{},
 		TxExecutionOrderHandler:      &commonMocks.TxExecutionOrderHandlerStub{},
 	}
```

### process/block/preprocess/transactions.go
```diff
@@ -344,7 +344,8 @@ func (txs *transactions) computeTxsToMe(
 
 	allTxs := make([]*txcache.WrappedTransaction, 0)
 	for _, miniBlock := range body.MiniBlocks {
-		shouldSkipMiniblock := miniBlock.SenderShardID == txs.shardCoordinator.SelfId() || !txs.isMiniBlockCorrect(miniBlock.Type)
+		shouldSkipMiniblock := miniBlock.SenderShardID == txs.shardCoordinator.SelfId() ||
+			!txs.isMiniBlockCorrect(miniBlock.Type)
 		if shouldSkipMiniblock {
 			continue
 		}
```

### process/block/preprocess/validatorInfoPreProcessor.go
```diff
@@ -259,7 +259,7 @@ func (vip *validatorInfoPreprocessor) ProcessMiniBlock(
 	if miniBlock.Type != block.PeerBlock {
 		return nil, indexOfLastTxProcessed, false, process.ErrWrongTypeInMiniBlock
 	}
-	if miniBlock.SenderShardID != core.MetachainShardId {
+	if miniBlock.SenderShardID != core.MetachainShardId || miniBlock.ReceiverShardID != core.AllShardId {
 		return nil, indexOfLastTxProcessed, false, process.ErrValidatorInfoMiniBlockNotFromMeta
 	}
 
```

### process/block/preprocess/validatorInfoPreProcessor_test.go
```diff
@@ -222,7 +222,7 @@ func TestNewValidatorInfoPreprocessor_ProcessMiniBlockShouldWork(t *testing.T) {
 	txHashes := make([][]byte, 0)
 	mb1 := block.MiniBlock{
 		TxHashes:        txHashes,
-		ReceiverShardID: 1,
+		ReceiverShardID: core.AllShardId,
 		SenderShardID:   core.MetachainShardId,
 		Type:            block.PeerBlock,
 	}
```

### process/coordinator/printDoubleTransactionsDetector.go
```diff
@@ -15,33 +15,34 @@ import (
 	logger "github.com/multiversx/mx-chain-logger-go"
 )
 
-const printReportHeader = "double transactions found (this is not critical, thus)\nshowing the whole block body:\n"
-const nilBlockBodyMessage = "nil block body in printDoubleTransactionsDetector.ProcessBlockBody"
+const printReportHeaderNotCritical = "double transactions found (this is not critical, thus)\nshowing the whole block body:\n"
+const printReportHeader = "double transactions found \nshowing the whole block body:\n"
+const nilBlockBodyMessage = "nil block body in doubleTransactionsDetector.ProcessBlockBody"
 const noDoubledTransactionsFoundMessage = "no double transactions found"
 const doubledTransactionsFoundButFlagActive = "double transactions found but this is expected until the AddFailedRelayedTxToInvalidMBsDisableEpoch is deactivated"
 
-// ArgsPrintDoubleTransactionsDetector is the argument DTO structure used in the NewPrintDoubleTransactionsDetector function
-type ArgsPrintDoubleTransactionsDetector struct {
+// ArgsDoubleTransactionsDetector is the argument DTO structure used in the NewDoubleTransactionsDetector function
+type ArgsDoubleTransactionsDetector struct {
 	Marshaller          marshal.Marshalizer
 	Hasher              hashing.Hasher
 	EnableEpochsHandler common.EnableEpochsHandler
 }
 
-type printDoubleTransactionsDetector struct {
+type doubleTransactionsDetector struct {
 	marshaller          marshal.Marshalizer
 	hasher              hashing.Hasher
 	logger              logger.Logger
 	enableEpochsHandler common.EnableEpochsHandler
 }
 
-// NewPrintDoubleTransactionsDetector creates a new instance of printDoubleTransactionsDetector
-func NewPrintDoubleTransactionsDetector(args ArgsPrintDoubleTransactionsDetector) (*printDoubleTransactionsDetector, error) {
-	err := checkArgsPrintDoubleTransactionsDetector(args)
+// NewDoubleTransactionsDetector creates a new instance of doubleTransactionsDetector
+func NewDoubleTransactionsDetector(args ArgsDoubleTransactionsDetector) (*doubleTransactionsDetector, error) {
+	err := checkArgsDoubleTransactionsDetector(args)
 	if err != nil {
 		return nil, err
 	}
 
-	detector := &printDoubleTransactionsDetector{
+	detector := &doubleTransactionsDetector{
 		marshaller:          args.Marshaller,
 		hasher:              args.Hasher,
 		enableEpochsHandler: args.EnableEpochsHandler,
@@ -51,7 +52,7 @@ func NewPrintDoubleTransactionsDetector(args ArgsPrintDoubleTransactionsDetector
 	return detector, nil
 }
 
-func checkArgsPrintDoubleTransactionsDetector(args ArgsPrintDoubleTransactionsDetector) error {
+func checkArgsDoubleTransactionsDetector(args ArgsDoubleTransactionsDetector) error {
 	if check.IfNil(args.Marshaller) {
 		return process.ErrNilMarshalizer
 	}
@@ -68,10 +69,10 @@ func checkArgsPrintDoubleTransactionsDetector(args ArgsPrintDoubleTransactionsDe
 
 // ProcessBlockBody processes the block body provided in search of doubled transactions. If there are doubled transactions,
 // this method will log as error the event providing as much information as possible
-func (detector *printDoubleTransactionsDetector) ProcessBlockBody(body *block.Body) {
+func (detector *doubleTransactionsDetector) ProcessBlockBody(body *block.Body) error {
 	if body == nil {
 		detector.logger.Error(nilBlockBodyMessage)
-		return
+		return nil
 	}
 
 	transactions := make(map[string]int)
@@ -99,17 +100,26 @@ func (detector *printDoubleTransactionsDetector) ProcessBlockBody(body *block.Bo
 
 	if !doubleTransactionsExist {
 		detector.logger.Debug(noDoubledTransactionsFoundMessage)
-		return
+		return nil
 	}
-	if detector.enableEpochsHandler.IsFlagEnabled(common.AddFailedRelayedTxToInvalidMBsFlag) {
-		detector.logger.Debug(doubledTransactionsFoundButFlagActive)
-		return
+
+	relayedV1V2Disabled := detector.enableEpochsHandler.IsFlagEnabled(common.RelayedTransactionsV1V2DisableFlag)
+
+	if !relayedV1V2Disabled {
+		if detector.enableEpochsHandler.IsFlagEnabled(common.AddFailedRelayedTxToInvalidMBsFlag) {
+			detector.logger.Debug(doubledTransactionsFoundButFlagActive)
+			return nil
+		}
+
+		detector.logger.Error(printReportHeaderNotCritical + printReport.String())
+		return nil
 	}
 
 	detector.logger.Error(printReportHeader + printReport.String())
+	return process.ErrDoubleTransactionsFound
 }
 
 // IsInterfaceNil returns true if there is no value under the interface
-func (detector *printDoubleTransactionsDetector) IsInterfaceNil() bool {
+func (detector *doubleTransactionsDetector) IsInterfaceNil() bool {
 	return detector == nil
 }
```

### process/coordinator/printDoubleTransactionsDetector_test.go
```diff
@@ -13,10 +13,11 @@ import (
 	"github.com/multiversx/mx-chain-go/testscommon/enableEpochsHandlerMock"
 	"github.com/multiversx/mx-chain-go/testscommon/marshallerMock"
 	"github.com/stretchr/testify/assert"
+	"github.com/stretchr/testify/require"
 )
 
-func createMockArgsPrintDoubleTransactionsDetector() ArgsPrintDoubleTransactionsDetector {
-	return ArgsPrintDoubleTransactionsDetector{
+func createMockArgsPrintDoubleTransactionsDetector() ArgsDoubleTransactionsDetector {
+	return ArgsDoubleTransactionsDetector{
 		Marshaller:          &marshallerMock.MarshalizerMock{},
 		Hasher:              &testscommon.HasherStub{},
 		EnableEpochsHandler: enableEpochsHandlerMock.NewEnableEpochsHandlerStub(),
@@ -32,7 +33,7 @@ func TestNewPrintDoubleTransactionsDetector(t *testing.T) {
 		args := createMockArgsPrintDoubleTransactionsDetector()
 		args.Marshaller = nil
 
-		detector, err := NewPrintDoubleTransactionsDetector(args)
+		detector, err := NewDoubleTransactionsDetector(args)
 		assert.True(t, check.IfNil(detector))
 		assert.Equal(t, process.ErrNilMarshalizer, err)
 	})
@@ -42,7 +43,7 @@ func TestNewPrintDoubleTransactionsDetector(t *testing.T) {
 		args := createMockArgsPrintDoubleTransactionsDetector()
 		args.Hasher = nil
 
-		detector, err := NewPrintDoubleTransactionsDetector(args)
+		detector, err := NewDoubleTransactionsDetector(args)
 		assert.True(t, check.IfNil(detector))
 		assert.Equal(t, process.ErrNilHasher, err)
 	})
@@ -52,7 +53,7 @@ func TestNewPrintDoubleTransactionsDetector(t *testing.T) {
 		args := createMockArgsPrintDoubleTransactionsDetector()
 		args.EnableEpochsHandler = nil
 
-		detector, err := NewPrintDoubleTransactionsDetector(args)
+		detector, err := NewDoubleTransactionsDetector(args)
 		assert.True(t, check.IfNil(detector))
 		assert.Equal(t, process.ErrNilEnableEpochsHandler, err)
 	})
@@ -62,7 +63,7 @@ func TestNewPrintDoubleTransactionsDetector(t *testing.T) {
 		args := createMockArgsPrintDoubleTransactionsDetector()
 		args.EnableEpochsHandler = enableEpochsHandlerMock.NewEnableEpochsHandlerStubWithNoFlagsDefined()
 
-		detector, err := NewPrintDoubleTransactionsDetector(args)
+		detector, err := NewDoubleTransactionsDetector(args)
 		assert.True(t, check.IfNil(detector))
 		assert.True(t, errors.Is(err, core.ErrInvalidEnableEpochsHandler))
 	})
@@ -71,7 +72,7 @@ func TestNewPrintDoubleTransactionsDetector(t *testing.T) {
 
 		args := createMockArgsPrintDoubleTransactionsDetector()
 
-		detector, err := NewPrintDoubleTransactionsDetector(args)
+		detector, err := NewDoubleTransactionsDetector(args)
 		assert.False(t, check.IfNil(detector))
 		assert.Nil(t, err)
 	})
@@ -85,22 +86,23 @@ func TestPrintDoubleTransactionsDetector_ProcessBlockBody(t *testing.T) {
 
 		errorCalled := false
 		args := createMockArgsPrintDoubleTransactionsDetector()
-		detector, _ := NewPrintDoubleTransactionsDetector(args)
+		detector, _ := NewDoubleTransactionsDetector(args)
 		detector.logger = &testscommon.LoggerStub{
 			ErrorCalled: func(message string, args ...interface{}) {
 				errorCalled = message == nilBlockBodyMessage
 			},
 		}
 
-		detector.ProcessBlockBody(nil)
+		err := detector.ProcessBlockBody(nil)
+		require.Nil(t, err)
 		assert.True(t, errorCalled)
 	})
 	t.Run("empty block body", func(t *testing.T) {
 		t.Parallel()
 
 		debugCalled := false
 		args := createMockArgsPrintDoubleTransactionsDetector()
-		detector, _ := NewPrintDoubleTransactionsDetector(args)
+		detector, _ := NewDoubleTransactionsDetector(args)
 		detector.logger = &testscommon.LoggerStub{
 			ErrorCalled: func(message string, args ...interface{}) {
 				assert.Fail(t, "should have not called error")
@@ -110,15 +112,16 @@ func TestPrintDoubleTransactionsDetector_ProcessBlockBody(t *testing.T) {
 			},
 		}
 
-		detector.ProcessBlockBody(&block.Body{})
+		err := detector.ProcessBlockBody(&block.Body{})
+		require.Nil(t, err)
 		assert.True(t, debugCalled)
 	})
 	t.Run("no doubled transactions", func(t *testing.T) {
 		t.Parallel()
 
 		debugCalled := false
 		args := createMockArgsPrintDoubleTransactionsDetector()
-		detector, _ := NewPrintDoubleTransactionsDetector(args)
+		detector, _ := NewDoubleTransactionsDetector(args)
 		detector.logger = &testscommon.LoggerStub{
 			ErrorCalled: func(message string, args ...interface{}) {
 				assert.Fail(t, "should have not called error")
@@ -138,7 +141,8 @@ func TestPrintDoubleTransactionsDetector_ProcessBlockBody(t *testing.T) {
 				},
 			},
 		}
-		detector.ProcessBlockBody(body)
+		err := detector.ProcessBlockBody(body)
+		require.Nil(t, err)
 		assert.True(t, debugCalled)
 	})
 	t.Run("doubled transactions in different miniblocks but feature not active", func(t *testing.T) {
@@ -147,7 +151,7 @@ func TestPrintDoubleTransactionsDetector_ProcessBlockBody(t *testing.T) {
 		debugCalled := false
 		args := createMockArgsPrintDoubleTransactionsDetector()
 		args.EnableEpochsHandler = enableEpochsHandlerMock.NewEnableEpochsHandlerStub(common.AddFailedRelayedTxToInvalidMBsFlag)
-		detector, _ := NewPrintDoubleTransactionsDetector(args)
+		detector, _ := NewDoubleTransactionsDetector(args)
 		detector.logger = &testscommon.LoggerStub{
 			ErrorCalled: func(message string, args ...interface{}) {
 				assert.Fail(t, "should have not called error")
@@ -167,22 +171,23 @@ func TestPrintDoubleTransactionsDetector_ProcessBlockBody(t *testing.T) {
 				},
 			},
 		}
-		detector.ProcessBlockBody(body)
+		err := detector.ProcessBlockBody(body)
+		require.Nil(t, err)
 		assert.True(t, debugCalled)
 	})
 	t.Run("doubled transactions in different miniblocks", func(t *testing.T) {
 		t.Parallel()
 
 		errorCalled := false
-		expectedMessage := printReportHeader + ` miniblock hash , type TxBlock, 0 -> 0
+		expectedMessage := printReportHeaderNotCritical + ` miniblock hash , type TxBlock, 0 -> 0
   tx hash 7478206861736831
   tx hash 7478206861736832
  miniblock hash , type TxBlock, 0 -> 0
   tx hash 7478206861736831
   tx hash 7478206861736834
 `
 		args := createMockArgsPrintDoubleTransactionsDetector()
-		detector, _ := NewPrintDoubleTransactionsDetector(args)
+		detector, _ := NewDoubleTransactionsDetector(args)
 		detector.logger = &testscommon.LoggerStub{
 			ErrorCalled: func(message string, args ...interface{}) {
 				assert.Equal(t, expectedMessage, message)
@@ -203,22 +208,23 @@ func TestPrintDoubleTransactionsDetector_ProcessBlockBody(t *testing.T) {
 				},
 			},
 		}
-		detector.ProcessBlockBody(body)
+		err := detector.ProcessBlockBody(body)
+		require.Nil(t, err)
 		assert.True(t, errorCalled)
 	})
 	t.Run("doubled transactions in same miniblock", func(t *testing.T) {
 		t.Parallel()
 
 		errorCalled := false
-		expectedMessage := printReportHeader + ` miniblock hash , type TxBlock, 0 -> 0
+		expectedMessage := printReportHeaderNotCritical + ` miniblock hash , type TxBlock, 0 -> 0
   tx hash 7478206861736831
   tx hash 7478206861736831
  miniblock hash , type TxBlock, 0 -> 0
   tx hash 7478206861736832
   tx hash 7478206861736834
 `
 		args := createMockArgsPrintDoubleTransactionsDetector()
-		detector, _ := NewPrintDoubleTransactionsDetector(args)
+		detector, _ := NewDoubleTransactionsDetector(args)
 		detector.logger = &testscommon.LoggerStub{
 			ErrorCalled: func(message string, args ...interface{}) {
 				assert.Equal(t, expectedMessage, message)
@@ -239,7 +245,8 @@ func TestPrintDoubleTransactionsDetector_ProcessBlockBody(t *testing.T) {
 				},
 			},
 		}
-		detector.ProcessBlockBody(body)
+		err := detector.ProcessBlockBody(body)
+		require.Nil(t, err)
 		assert.True(t, errorCalled)
 	})
 }
```

### process/coordinator/process.go
```diff
@@ -441,7 +441,10 @@ func (tc *transactionCoordinator) ProcessBlockTransaction(
 		return timeRemaining() >= 0
 	}
 
-	tc.doubleTransactionsDetector.ProcessBlockBody(body)
+	err := tc.doubleTransactionsDetector.ProcessBlockBody(body)
+	if err != nil {
+		return err
+	}
 
 	startTime := time.Now()
 	mbIndex, err := tc.processMiniBlocksToMe(header, body, haveTime)
@@ -477,6 +480,11 @@ func (tc *transactionCoordinator) processMiniBlocksFromMe(
 	haveTime func() bool,
 ) error {
 	for _, mb := range body.MiniBlocks {
+		err := tc.checkMiniBlock(mb)
+		if err != nil {
+			return err
+		}
+
 		if mb.SenderShardID != tc.shardCoordinator.SelfId() {
 			return process.ErrMiniBlocksInWrongOrder
 		}
@@ -516,6 +524,38 @@ func (tc *transactionCoordinator) processMiniBlocksFromMe(
 	return nil
 }
 
+func (tc *transactionCoordinator) checkMiniBlock(
+	miniBlock *block.MiniBlock,
+) error {
+	// there are checks for non existing shard id at interceptors level
+
+	if miniBlock.SenderShardID != tc.shardCoordinator.SelfId() && miniBlock.ReceiverShardID != tc.shardCoordinator.SelfId() && miniBlock.ReceiverShardID != core.AllShardId {
+		return fmt.Errorf("%w - not valid shard ids: block type: %s, sender shard id: %d, receiver shard id: %d",
+			process.ErrInvalidShardId,
+			miniBlock.Type,
+			miniBlock.SenderShardID,
+			miniBlock.ReceiverShardID)
+	}
+
+	if miniBlock.GetType() == block.PeerBlock && miniBlock.GetReceiverShardID() != core.AllShardId {
+		return fmt.Errorf("%w - peer blocks receiver shard ID: block type: %s, sender shard id: %d, receiver shard id: %d",
+			process.ErrInvalidShardId,
+			miniBlock.Type,
+			miniBlock.SenderShardID,
+			miniBlock.ReceiverShardID)
+	}
+
+	if miniBlock.GetType() != block.PeerBlock && miniBlock.ReceiverShardID == core.AllShardId {
+		return fmt.Errorf("%w - invalid all shard ids: block type: %s, sender shard id: %d, receiver shard id: %d",
+			process.ErrInvalidShardId,
+			miniBlock.Type,
+			miniBlock.SenderShardID,
+			miniBlock.ReceiverShardID)
+	}
+
+	return nil
+}
+
 func (tc *transactionCoordinator) processMiniBlocksToMe(
 	header data.HeaderHandler,
 	body *block.Body,
@@ -537,17 +577,31 @@ func (tc *transactionCoordinator) processMiniBlocksToMe(
 	mbIndex := 0
 	for mbIndex = 0; mbIndex < len(body.MiniBlocks); mbIndex++ {
 		miniBlock := body.MiniBlocks[mbIndex]
+
+		err := tc.checkMiniBlock(miniBlock)
+		if err != nil {
+			return mbIndex, err
+		}
+
 		if miniBlock.SenderShardID == tc.shardCoordinator.SelfId() {
 			return mbIndex, nil
 		}
 
+		if miniBlock.GetType() != block.PeerBlock && miniBlock.ReceiverShardID != tc.shardCoordinator.SelfId() {
+			return mbIndex, fmt.Errorf("%w: block type: %s, sender shard id: %d, receiver shard id: %d",
+				process.ErrInvalidShardId,
+				miniBlock.Type,
+				miniBlock.SenderShardID,
+				miniBlock.ReceiverShardID)
+		}
+
 		preProc := tc.getPreProcessor(miniBlock.Type)
 		if check.IfNil(preProc) {
 			return mbIndex, process.ErrMissingPreProcessor
 		}
 
 		log.Debug("processMiniBlocksToMe: miniblock", "type", miniBlock.Type)
-		err := preProc.ProcessBlockTransactions(header, &block.Body{MiniBlocks: []*block.MiniBlock{miniBlock}}, haveTime)
+		err = preProc.ProcessBlockTransactions(header, &block.Body{MiniBlocks: []*block.MiniBlock{miniBlock}}, haveTime)
 		if err != nil {
 			return mbIndex, err
 		}
```

### process/coordinator/process_test.go
```diff
@@ -245,7 +245,7 @@ func createMockTransactionCoordinatorArguments() ArgTransactionCoordinator {
 		TransactionsLogProcessor:     &mock.TxLogsProcessorStub{},
 		EnableEpochsHandler:          enableEpochsHandlerMock.NewEnableEpochsHandlerStub(),
 		ScheduledTxsExecutionHandler: &testscommon.ScheduledTxsExecutionStub{},
-		DoubleTransactionsDetector:   &testscommon.PanicDoubleTransactionsDetector{},
+		DoubleTransactionsDetector:   &testscommon.DoubleTransactionsDetector{},
 		ProcessedMiniBlocksTracker:   &testscommon.ProcessedMiniBlocksTrackerStub{},
 		TxExecutionOrderHandler:      &commonMock.TxExecutionOrderHandlerStub{},
 	}
@@ -1824,26 +1824,28 @@ func TestTransactionCoordinator_ProcessBlockTransactionProcessTxError(t *testing
 	err = tc.ProcessBlockTransaction(&block.Header{}, &block.Body{}, haveTime)
 	assert.Nil(t, err)
 
+	selfShardID := tc.shardCoordinator.SelfId()
+
 	body := &block.Body{}
-	miniBlock := &block.MiniBlock{SenderShardID: 1, ReceiverShardID: 0, Type: block.TxBlock, TxHashes: [][]byte{txHash}}
+	miniBlock := &block.MiniBlock{SenderShardID: 1, ReceiverShardID: selfShardID, Type: block.TxBlock, TxHashes: [][]byte{txHash}}
 	miniBlockHash1, _ := core.CalculateHash(tc.marshalizer, tc.hasher, miniBlock)
 	body.MiniBlocks = append(body.MiniBlocks, miniBlock)
 
 	tc.RequestBlockTransactions(body)
-	err = tc.ProcessBlockTransaction(&block.Header{MiniBlockHeaders: []block.MiniBlockHeader{{Hash: miniBlockHash1, TxCount: 1}}}, body, haveTime)
+	err = tc.ProcessBlockTransaction(&block.Header{MiniBlockHeaders: []block.MiniBlockHeader{{Hash: miniBlockHash1, TxCount: 1, ReceiverShardID: selfShardID}}}, body, haveTime)
 	assert.Equal(t, process.ErrHigherNonceInTransaction, err)
 
 	noTime := func() time.Duration {
 		return 0
 	}
-	err = tc.ProcessBlockTransaction(&block.Header{MiniBlockHeaders: []block.MiniBlockHeader{{Hash: miniBlockHash1, TxCount: 1}}}, body, noTime)
+	err = tc.ProcessBlockTransaction(&block.Header{MiniBlockHeaders: []block.MiniBlockHeader{{Hash: miniBlockHash1, TxCount: 1, ReceiverShardID: selfShardID}}}, body, noTime)
 	assert.Equal(t, process.ErrHigherNonceInTransaction, err)
 
 	txHashToAsk := []byte("tx_hashnotinPool")
 	miniBlock = &block.MiniBlock{SenderShardID: 0, ReceiverShardID: 0, Type: block.TxBlock, TxHashes: [][]byte{txHashToAsk}}
 	miniBlockHash2, _ := core.CalculateHash(tc.marshalizer, tc.hasher, miniBlock)
 	body.MiniBlocks = append(body.MiniBlocks, miniBlock)
-	err = tc.ProcessBlockTransaction(&block.Header{MiniBlockHeaders: []block.MiniBlockHeader{{Hash: miniBlockHash1, TxCount: 1}, {Hash: miniBlockHash2, TxCount: 1}}}, body, haveTime)
+	err = tc.ProcessBlockTransaction(&block.Header{MiniBlockHeaders: []block.MiniBlockHeader{{Hash: miniBlockHash1, TxCount: 1, ReceiverShardID: selfShardID}, {Hash: miniBlockHash2, TxCount: 1, ReceiverShardID: selfShardID}}}, body, haveTime)
 	assert.Equal(t, process.ErrHigherNonceInTransaction, err)
 }
 
@@ -2659,7 +2661,7 @@ func TestTransactionCoordinator_VerifyCreatedMiniBlocksShouldReturnWhenEpochIsNo
 			},
 		},
 		ScheduledTxsExecutionHandler: &testscommon.ScheduledTxsExecutionStub{},
-		DoubleTransactionsDetector:   &testscommon.PanicDoubleTransactionsDetector{},
+		DoubleTransactionsDetector:   &testscommon.DoubleTransactionsDetector{},
 		ProcessedMiniBlocksTracker:   &testscommon.ProcessedMiniBlocksTrackerStub{},
 		TxExecutionOrderHandler:      &commonMock.TxExecutionOrderHandlerStub{},
 	}
@@ -2709,7 +2711,7 @@ func TestTransactionCoordinator_VerifyCreatedMiniBlocksShouldErrMaxGasLimitPerMi
 		TransactionsLogProcessor:     &mock.TxLogsProcessorStub{},
 		EnableEpochsHandler:          enableEpochsHandlerMock.NewEnableEpochsHandlerStub(),
 		ScheduledTxsExecutionHandler: &testscommon.ScheduledTxsExecutionStub{},
-		DoubleTransactionsDetector:   &testscommon.PanicDoubleTransactionsDetector{},
+		DoubleTransactionsDetector:   &testscommon.DoubleTransactionsDetector{},
 		ProcessedMiniBlocksTracker:   &testscommon.ProcessedMiniBlocksTrackerStub{},
 		TxExecutionOrderHandler:      &commonMock.TxExecutionOrderHandlerStub{},
 	}
@@ -2783,7 +2785,7 @@ func TestTransactionCoordinator_VerifyCreatedMiniBlocksShouldErrMaxAccumulatedFe
 		TransactionsLogProcessor:     &mock.TxLogsProcessorStub{},
 		EnableEpochsHandler:          enableEpochsHandlerMock.NewEnableEpochsHandlerStub(),
 		ScheduledTxsExecutionHandler: &testscommon.ScheduledTxsExecutionStub{},
-		DoubleTransactionsDetector:   &testscommon.PanicDoubleTransactionsDetector{},
+		DoubleTransactionsDetector:   &testscommon.DoubleTransactionsDetector{},
 		ProcessedMiniBlocksTracker:   &testscommon.ProcessedMiniBlocksTrackerStub{},
 		TxExecutionOrderHandler:      &commonMock.TxExecutionOrderHandlerStub{},
 	}
@@ -2862,7 +2864,7 @@ func TestTransactionCoordinator_VerifyCreatedMiniBlocksShouldErrMaxDeveloperFees
 		TransactionsLogProcessor:     &mock.TxLogsProcessorStub{},
 		EnableEpochsHandler:          enableEpochsHandlerMock.NewEnableEpochsHandlerStub(),
 		ScheduledTxsExecutionHandler: &testscommon.ScheduledTxsExecutionStub{},
-		DoubleTransactionsDetector:   &testscommon.PanicDoubleTransactionsDetector{},
+		DoubleTransactionsDetector:   &testscommon.DoubleTransactionsDetector{},
 		ProcessedMiniBlocksTracker:   &testscommon.ProcessedMiniBlocksTrackerStub{},
 		TxExecutionOrderHandler:      &commonMock.TxExecutionOrderHandlerStub{},
 	}
@@ -2941,7 +2943,7 @@ func TestTransactionCoordinator_VerifyCreatedMiniBlocksShouldWork(t *testing.T)
 		TransactionsLogProcessor:     &mock.TxLogsProcessorStub{},
 		EnableEpochsHandler:          enableEpochsHandlerMock.NewEnableEpochsHandlerStub(),
 		ScheduledTxsExecutionHandler: &testscommon.ScheduledTxsExecutionStub{},
-		DoubleTransactionsDetector:   &testscommon.PanicDoubleTransactionsDetector{},
+		DoubleTransactionsDetector:   &testscommon.DoubleTransactionsDetector{},
 		ProcessedMiniBlocksTracker:   &testscommon.ProcessedMiniBlocksTrackerStub{},
 		TxExecutionOrderHandler:      &commonMock.TxExecutionOrderHandlerStub{},
 	}
@@ -3003,7 +3005,7 @@ func TestTransactionCoordinator_GetAllTransactionsShouldWork(t *testing.T) {
 		TransactionsLogProcessor:     &mock.TxLogsProcessorStub{},
 		EnableEpochsHandler:          enableEpochsHandlerMock.NewEnableEpochsHandlerStub(),
 		ScheduledTxsExecutionHandler: &testscommon.ScheduledTxsExecutionStub{},
-		DoubleTransactionsDetector:   &testscommon.PanicDoubleTransactionsDetector{},
+		DoubleTransactionsDetector:   &testscommon.DoubleTransactionsDetector{},
 		ProcessedMiniBlocksTracker:   &testscommon.ProcessedMiniBlocksTrackerStub{},
 		TxExecutionOrderHandler:      &commonMock.TxExecutionOrderHandlerStub{},
 	}
@@ -3088,7 +3090,7 @@ func TestTransactionCoordinator_VerifyGasLimitShouldErrMaxGasLimitPerMiniBlockIn
 		TransactionsLogProcessor:     &mock.TxLogsProcessorStub{},
 		EnableEpochsHandler:          enableEpochsHandlerMock.NewEnableEpochsHandlerStub(),
 		ScheduledTxsExecutionHandler: &testscommon.ScheduledTxsExecutionStub{},
-		DoubleTransactionsDetector:   &testscommon.PanicDoubleTransactionsDetector{},
+		DoubleTransactionsDetector:   &testscommon.DoubleTransactionsDetector{},
 		ProcessedMiniBlocksTracker:   &testscommon.ProcessedMiniBlocksTrackerStub{},
 		TxExecutionOrderHandler:      &commonMock.TxExecutionOrderHandlerStub{},
 	}
@@ -3183,7 +3185,7 @@ func TestTransactionCoordinator_VerifyGasLimitShouldWork(t *testing.T) {
 		TransactionsLogProcessor:     &mock.TxLogsProcessorStub{},
 		EnableEpochsHandler:          enableEpochsHandlerMock.NewEnableEpochsHandlerStub(),
 		ScheduledTxsExecutionHandler: &testscommon.ScheduledTxsExecutionStub{},
-		DoubleTransactionsDetector:   &testscommon.PanicDoubleTransactionsDetector{},
+		DoubleTransactionsDetector:   &testscommon.DoubleTransactionsDetector{},
 		ProcessedMiniBlocksTracker:   &testscommon.ProcessedMiniBlocksTrackerStub{},
 		TxExecutionOrderHandler:      &commonMock.TxExecutionOrderHandlerStub{},
 	}
@@ -3264,7 +3266,7 @@ func TestTransactionCoordinator_CheckGasProvidedByMiniBlockInReceiverShardShould
 		TransactionsLogProcessor:     &mock.TxLogsProcessorStub{},
 		EnableEpochsHandler:          enableEpochsHandlerMock.NewEnableEpochsHandlerStub(),
 		ScheduledTxsExecutionHandler: &testscommon.ScheduledTxsExecutionStub{},
-		DoubleTransactionsDetector:   &testscommon.PanicDoubleTransactionsDetector{},
+		DoubleTransactionsDetector:   &testscommon.DoubleTransactionsDetector{},
 		ProcessedMiniBlocksTracker:   &testscommon.ProcessedMiniBlocksTrackerStub{},
 		TxExecutionOrderHandler:      &commonMock.TxExecutionOrderHandlerStub{},
 	}
@@ -3316,7 +3318,7 @@ func TestTransactionCoordinator_CheckGasProvidedByMiniBlockInReceiverShardShould
 		TransactionsLogProcessor:     &mock.TxLogsProcessorStub{},
 		EnableEpochsHandler:          enableEpochsHandlerMock.NewEnableEpochsHandlerStub(),
 		ScheduledTxsExecutionHandler: &testscommon.ScheduledTxsExecutionStub{},
-		DoubleTransactionsDetector:   &testscommon.PanicDoubleTransactionsDetector{},
+		DoubleTransactionsDetector:   &testscommon.DoubleTransactionsDetector{},
 		ProcessedMiniBlocksTracker:   &testscommon.ProcessedMiniBlocksTrackerStub{},
 		TxExecutionOrderHandler:      &commonMock.TxExecutionOrderHandlerStub{},
 	}
@@ -3375,7 +3377,7 @@ func TestTransactionCoordinator_CheckGasProvidedByMiniBlockInReceiverShardShould
 		TransactionsLogProcessor:     &mock.TxLogsProcessorStub{},
 		EnableEpochsHandler:          enableEpochsHandlerMock.NewEnableEpochsHandlerStub(),
 		ScheduledTxsExecutionHandler: &testscommon.ScheduledTxsExecutionStub{},
-		DoubleTransactionsDetector:   &testscommon.PanicDoubleTransactionsDetector{},
+		DoubleTransactionsDetector:   &testscommon.DoubleTransactionsDetector{},
 		ProcessedMiniBlocksTracker:   &testscommon.ProcessedMiniBlocksTrackerStub{},
 		TxExecutionOrderHandler:      &commonMock.TxExecutionOrderHandlerStub{},
 	}
@@ -3441,7 +3443,7 @@ func TestTransactionCoordinator_CheckGasProvidedByMiniBlockInReceiverShardShould
 		TransactionsLogProcessor:     &mock.TxLogsProcessorStub{},
 		EnableEpochsHandler:          enableEpochsHandlerMock.NewEnableEpochsHandlerStub(),
 		ScheduledTxsExecutionHandler: &testscommon.ScheduledTxsExecutionStub{},
-		DoubleTransactionsDetector:   &testscommon.PanicDoubleTransactionsDetector{},
+		DoubleTransactionsDetector:   &testscommon.DoubleTransactionsDetector{},
 		ProcessedMiniBlocksTracker:   &testscommon.ProcessedMiniBlocksTrackerStub{},
 		TxExecutionOrderHandler:      &commonMock.TxExecutionOrderHandlerStub{},
 	}
@@ -3510,7 +3512,7 @@ func TestTransactionCoordinator_CheckGasProvidedByMiniBlockInReceiverShardShould
 		TransactionsLogProcessor:     &mock.TxLogsProcessorStub{},
 		EnableEpochsHandler:          enableEpochsHandlerMock.NewEnableEpochsHandlerStub(),
 		ScheduledTxsExecutionHandler: &testscommon.ScheduledTxsExecutionStub{},
-		DoubleTransactionsDetector:   &testscommon.PanicDoubleTransactionsDetector{},
+		DoubleTransactionsDetector:   &testscommon.DoubleTransactionsDetector{},
 		ProcessedMiniBlocksTracker:   &testscommon.ProcessedMiniBlocksTrackerStub{},
 		TxExecutionOrderHandler:      &commonMock.TxExecutionOrderHandlerStub{},
 	}
@@ -3566,7 +3568,7 @@ func TestTransactionCoordinator_VerifyFeesShouldErrMissingTransaction(t *testing
 		TransactionsLogProcessor:     &mock.TxLogsProcessorStub{},
 		EnableEpochsHandler:          enableEpochsHandlerMock.NewEnableEpochsHandlerStub(),
 		ScheduledTxsExecutionHandler: &testscommon.ScheduledTxsExecutionStub{},
-		DoubleTransactionsDetector:   &testscommon.PanicDoubleTransactionsDetector{},
+		DoubleTransactionsDetector:   &testscommon.DoubleTransactionsDetector{},
 		ProcessedMiniBlocksTracker:   &testscommon.ProcessedMiniBlocksTrackerStub{},
 		TxExecutionOrderHandler:      &commonMock.TxExecutionOrderHandlerStub{},
 	}
@@ -3627,7 +3629,7 @@ func TestTransactionCoordinator_VerifyFeesShouldErrMaxAccumulatedFeesExceeded(t
 		TransactionsLogProcessor:     &mock.TxLogsProcessorStub{},
 		EnableEpochsHandler:          enableEpochsHandlerMock.NewEnableEpochsHandlerStub(),
 		ScheduledTxsExecutionHandler: &testscommon.ScheduledTxsExecutionStub{},
-		DoubleTransactionsDetector:   &testscommon.PanicDoubleTransactionsDetector{},
+		DoubleTransactionsDetector:   &testscommon.DoubleTransactionsDetector{},
 		ProcessedMiniBlocksTracker:   &testscommon.ProcessedMiniBlocksTrackerStub{},
 		TxExecutionOrderHandler:      &commonMock.TxExecutionOrderHandlerStub{},
 	}
@@ -3698,7 +3700,7 @@ func TestTransactionCoordinator_VerifyFeesShouldErrMaxDeveloperFeesExceeded(t *t
 		TransactionsLogProcessor:     &mock.TxLogsProcessorStub{},
 		EnableEpochsHandler:          enableEpochsHandlerMock.NewEnableEpochsHandlerStub(),
 		ScheduledTxsExecutionHandler: &testscommon.ScheduledTxsExecutionStub{},
-		DoubleTransactionsDetector:   &testscommon.PanicDoubleTransactionsDetector{},
+		DoubleTransactionsDetector:   &testscommon.DoubleTransactionsDetector{},
 		ProcessedMiniBlocksTracker:   &testscommon.ProcessedMiniBlocksTrackerStub{},
 		TxExecutionOrderHandler:      &commonMock.TxExecutionOrderHandlerStub{},
 	}
@@ -3777,7 +3779,7 @@ func TestTransactionCoordinator_VerifyFeesShouldErrMaxAccumulatedFeesExceededWhe
 				}
 			},
 		},
-		DoubleTransactionsDetector: &testscommon.PanicDoubleTransactionsDetector{},
+		DoubleTransactionsDetector: &testscommon.DoubleTransactionsDetector{},
 		ProcessedMiniBlocksTracker: &testscommon.ProcessedMiniBlocksTrackerStub{},
 		TxExecutionOrderHandler:    &commonMock.TxExecutionOrderHandlerStub{},
 	}
@@ -3863,7 +3865,7 @@ func TestTransactionCoordinator_VerifyFeesShouldErrMaxDeveloperFeesExceededWhenS
 				}
 			},
 		},
-		DoubleTransactionsDetector: &testscommon.PanicDoubleTransactionsDetector{},
+		DoubleTransactionsDetector: &testscommon.DoubleTransactionsDetector{},
 		ProcessedMiniBlocksTracker: &testscommon.ProcessedMiniBlocksTrackerStub{},
 		TxExecutionOrderHandler:    &commonMock.TxExecutionOrderHandlerStub{},
 	}
@@ -3949,7 +3951,7 @@ func TestTransactionCoordinator_VerifyFeesShouldWork(t *testing.T) {
 				}
 			},
 		},
-		DoubleTransactionsDetector: &testscommon.PanicDoubleTransactionsDetector{},
+		DoubleTransactionsDetector: &testscommon.DoubleTransactionsDetector{},
 		ProcessedMiniBlocksTracker: &testscommon.ProcessedMiniBlocksTrackerStub{},
 		TxExecutionOrderHandler:    &commonMock.TxExecutionOrderHandlerStub{},
 	}
@@ -4027,7 +4029,7 @@ func TestTransactionCoordinator_GetMaxAccumulatedAndDeveloperFeesShouldErr(t *te
 		TransactionsLogProcessor:     &mock.TxLogsProcessorStub{},
 		EnableEpochsHandler:          enableEpochsHandlerMock.NewEnableEpochsHandlerStub(),
 		ScheduledTxsExecutionHandler: &testscommon.ScheduledTxsExecutionStub{},
-		DoubleTransactionsDetector:   &testscommon.PanicDoubleTransactionsDetector{},
+		DoubleTransactionsDetector:   &testscommon.DoubleTransactionsDetector{},
 		ProcessedMiniBlocksTracker:   &testscommon.ProcessedMiniBlocksTrackerStub{},
 		TxExecutionOrderHandler:      &commonMock.TxExecutionOrderHandlerStub{},
 	}
@@ -4085,7 +4087,7 @@ func TestTransactionCoordinator_GetMaxAccumulatedAndDeveloperFeesShouldWork(t *t
 		TransactionsLogProcessor:     &mock.TxLogsProcessorStub{},
 		EnableEpochsHandler:          enableEpochsHandlerMock.NewEnableEpochsHandlerStub(),
 		ScheduledTxsExecutionHandler: &testscommon.ScheduledTxsExecutionStub{},
-		DoubleTransactionsDetector:   &testscommon.PanicDoubleTransactionsDetector{},
+		DoubleTransactionsDetector:   &testscommon.DoubleTransactionsDetector{},
 		ProcessedMiniBlocksTracker:   &testscommon.ProcessedMiniBlocksTrackerStub{},
 		TxExecutionOrderHandler:      &commonMock.TxExecutionOrderHandlerStub{},
 	}
@@ -4157,7 +4159,7 @@ func TestTransactionCoordinator_RevertIfNeededShouldWork(t *testing.T) {
 		TransactionsLogProcessor:     &mock.TxLogsProcessorStub{},
 		EnableEpochsHandler:          enableEpochsHandlerMock.NewEnableEpochsHandlerStub(),
 		ScheduledTxsExecutionHandler: &testscommon.ScheduledTxsExecutionStub{},
-		DoubleTransactionsDetector:   &testscommon.PanicDoubleTransactionsDetector{},
+		DoubleTransactionsDetector:   &testscommon.DoubleTransactionsDetector{},
 		ProcessedMiniBlocksTracker:   &testscommon.ProcessedMiniBlocksTrackerStub{},
 		TxExecutionOrderHandler:      &commonMock.TxExecutionOrderHandlerStub{},
 	}
```
