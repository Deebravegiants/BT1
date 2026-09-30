# [?] Added panic to flow Genesis and removed returning error. Fixed usages

## Summary
Severity: Unknown
Chain: Flow
Component: onflow/flow-go
Published: 2025-07-15
Source: https://github.com/onflow/flow-go/commit/956346e58133220c307d29269e81bf81609a6be6
Type: security-commit

## Details
Added panic to flow Genesis and removed returning error. Fixed usages

## Patch
### admin/commands/storage/backfill_tx_error_messages_test.go
```diff
@@ -80,8 +80,7 @@ func (suite *BackfillTxErrorMessagesSuite) SetupTest() {
 	suite.blockCount = 5
 	suite.blockHeadersMap = make(map[uint64]*flow.Header, suite.blockCount)
 
-	root, err := flow.Genesis(flow.Emulator)
-	require.NoError(suite.T(), err)
+	root := flow.Genesis(flow.Emulator)
 	suite.nodeRootBlock = root
 	suite.blockHeadersMap[suite.nodeRootBlock.Header.Height] = suite.nodeRootBlock.ToHeader()
 
@@ -134,6 +133,7 @@ func (suite *BackfillTxErrorMessagesSuite) SetupTest() {
 		nil,
 	)
 
+	var err error
 	suite.backend, err = backend.New(backend.Params{
 		State:                      suite.state,
 		ExecutionReceipts:          suite.receipts,
```

### engine/access/ingestion/engine_test.go
```diff
@@ -137,9 +137,7 @@ func (s *Suite) SetupTest() {
 
 	blockCount := 5
 	s.blockMap = make(map[uint64]*flow.Block, blockCount)
-	var err error
-	s.rootBlock, err = flow.Genesis(flow.Emulator)
-	require.NoError(s.T(), err)
+	s.rootBlock = flow.Genesis(flow.Emulator)
 	parent := s.rootBlock.ToHeader()
 
 	for i := 0; i < blockCount; i++ {
@@ -169,6 +167,7 @@ func (s *Suite) SetupTest() {
 	header := unittest.BlockHeaderFixture(unittest.WithHeaderHeight(0))
 	s.proto.params.On("FinalizedRoot").Return(header, nil)
 
+	var err error
 	s.collectionExecutedMetric, err = indexer.NewCollectionExecutedMetricImpl(
 		s.log,
 		metrics.NewNoopCollector(),
```

### engine/access/ingestion/tx_error_messages/tx_error_messages_core_test.go
```diff
@@ -74,10 +74,7 @@ func (s *TxErrorMessagesCoreSuite) SetupTest() {
 	s.connFactory = connectionmock.NewConnectionFactory(s.T())
 	s.receipts = storage.NewExecutionReceipts(s.T())
 	s.txErrorMessages = storage.NewTransactionResultErrorMessages(s.T())
-
-	var err error
-	s.rootBlock, err = flow.Genesis(flow.Emulator)
-	require.NoError(s.T(), err)
+	s.rootBlock = flow.Genesis(flow.Emulator)
 	s.finalizedBlock = unittest.BlockWithParentFixture(s.rootBlock.ToHeader()).ToHeader()
 
 	s.proto.state.On("Params").Return(s.proto.params)
```

### engine/access/ingestion/tx_error_messages/tx_error_messages_engine_test.go
```diff
@@ -89,9 +89,7 @@ func (s *TxErrorMessagesEngineSuite) SetupTest() {
 
 	blockCount := 5
 	s.blockMap = make(map[uint64]*flow.Block, blockCount)
-	var err error
-	s.rootBlock, err = flow.Genesis(flow.Emulator)
-	require.NoError(s.T(), err)
+	s.rootBlock = flow.Genesis(flow.Emulator)
 	parent := s.rootBlock.ToHeader()
 
 	for i := 0; i < blockCount; i++ {
```

### engine/access/rest/websockets/data_providers/account_statuses_provider_test.go
```diff
@@ -45,13 +45,8 @@ func TestNewAccountStatusesDataProvider(t *testing.T) {
 func (s *AccountStatusesProviderSuite) SetupTest() {
 	s.log = unittest.Logger()
 	s.api = ssmock.NewAPI(s.T())
-
 	s.chain = flow.Testnet.Chain()
-
-	var err error
-	s.rootBlock, err = flow.Genesis(s.chain.ChainID())
-	require.NoError(s.T(), err)
-
+	s.rootBlock = flow.Genesis(s.chain.ChainID())
 	s.factory = NewDataProviderFactory(
 		s.log,
 		s.api,
```

### engine/access/rest/websockets/data_providers/blocks_provider_test.go
```diff
@@ -53,10 +53,7 @@ func (s *BlocksProviderSuite) SetupTest() {
 
 	blockCount := 5
 	s.blocks = make([]*flow.Block, 0, blockCount)
-
-	var err error
-	s.rootBlock, err = flow.Genesis(flow.Emulator)
-	s.Require().NoError(err)
+	s.rootBlock = flow.Genesis(flow.Emulator)
 	parent := s.rootBlock.ToHeader()
 
 	for i := 0; i < blockCount; i++ {
```

### engine/access/rest/websockets/data_providers/events_provider_test.go
```diff
@@ -44,13 +44,8 @@ func TestEventsProviderSuite(t *testing.T) {
 func (s *EventsProviderSuite) SetupTest() {
 	s.log = unittest.Logger()
 	s.api = ssmock.NewAPI(s.T())
-
 	s.chain = flow.Testnet.Chain()
-
-	var err error
-	s.rootBlock, err = flow.Genesis(s.chain.ChainID())
-	s.Require().NoError(err)
-
+	s.rootBlock = flow.Genesis(s.chain.ChainID())
 	s.factory = NewDataProviderFactory(
 		s.log,
 		s.api,
```

### engine/access/rest/websockets/data_providers/transaction_statuses_provider_test.go
```diff
@@ -46,13 +46,8 @@ func (s *TransactionStatusesProviderSuite) SetupTest() {
 	s.log = unittest.Logger()
 	s.api = accessmock.NewAPI(s.T())
 	s.linkGenerator = mockcommonmodels.NewLinkGenerator(s.T())
-
 	s.chain = flow.Testnet.Chain()
-
-	var err error
-	s.rootBlock, err = flow.Genesis(s.chain.ChainID())
-	s.Require().NoError(err)
-
+	s.rootBlock = flow.Genesis(s.chain.ChainID())
 	s.factory = NewDataProviderFactory(
 		s.log,
 		nil,
```

### fvm/bootstrap.go
```diff
@@ -336,11 +336,7 @@ func (b *bootstrapExecutor) Preprocess() error {
 
 func (b *bootstrapExecutor) Execute() error {
 	if b.rootBlock == nil {
-		rootblock, err := flow.Genesis(b.ctx.Chain.ChainID())
-		if err != nil {
-			return fmt.Errorf("could not build genesis block: %w", err)
-		}
-		b.rootBlock = rootblock.ToHeader()
+		b.rootBlock = flow.Genesis(b.ctx.Chain.ChainID()).ToHeader()
 	}
 
 	// initialize the account addressing state
```

### integration/internal/emulator/ledger.go
```diff
@@ -44,10 +44,7 @@ func configureLedger(
 		}
 
 		// commit the genesis block to storage
-		genesis, err := flowgo.Genesis(conf.GetChainID())
-		if err != nil {
-			return nil, nil, fmt.Errorf("failed to generate genesis block: %w", err)
-		}
+		genesis := flowgo.Genesis(conf.GetChainID())
 		latestBlock = *genesis
 
 		err = store.CommitBlock(
```

### model/flow/block.go
```diff
@@ -7,7 +7,7 @@ import (
 	"github.com/vmihailenco/msgpack/v4"
 )
 
-func Genesis(chainID ChainID) (*Block, error) {
+func Genesis(chainID ChainID) *Block {
 	// create the raw content for the genesis block
 	payload := Payload{}
 
@@ -20,11 +20,11 @@ func Genesis(chainID ChainID) (*Block, error) {
 		View:      0,
 	})
 	if err != nil {
-		return nil, fmt.Errorf("failed to create root header body: %w", err)
+		panic(fmt.Errorf("failed to create genesis header body: %w", err))
 	}
 
 	// combine to block
-	return NewBlock(*headerBody, payload), nil
+	return NewBlock(*headerBody, payload)
 }
 
 // Block (currently) includes the all block header metadata and the payload content.
```

### model/flow/block_test.go
```diff
@@ -14,8 +14,7 @@ import (
 )
 
 func TestGenesisEncodingJSON(t *testing.T) {
-	genesis, err := flow.Genesis(flow.Mainnet)
-	require.NoError(t, err)
+	genesis := flow.Genesis(flow.Mainnet)
 	genesisID := genesis.ID()
 	data, err := json.Marshal(genesis)
 	require.NoError(t, err)
@@ -28,8 +27,7 @@ func TestGenesisEncodingJSON(t *testing.T) {
 }
 
 func TestGenesisDecodingMsgpack(t *testing.T) {
-	genesis, err := flow.Genesis(flow.Mainnet)
-	require.NoError(t, err)
+	genesis := flow.Genesis(flow.Mainnet)
 	genesisID := genesis.ID()
 	data, err := msgpack.Marshal(genesis)
 	require.NoError(t, err)
```
