# [?] fix panics during startup from incorrect nil checks

## Summary
Severity: Unknown
Chain: Flow
Component: onflow/flow-go
Published: 2026-02-12
Source: https://github.com/onflow/flow-go/commit/e2a3168030aafb8fe89e4791a71db11e16ef1bc0
Type: security-commit

## Details
fix panics during startup from incorrect nil checks

## Patch
### cmd/access/node_builder/access_node_builder.go
```diff
@@ -2204,8 +2204,8 @@ func (builder *FlowAccessNodeBuilder) Build() (cmd.Node, error) {
 
 			builder.nodeBackend, err = backend.New(backend.Params{
 				State:                 node.State,
-				CollectionRPC:         builder.CollectionRPC, // might be nil
-				HistoricalAccessNodes: utils.NotNil(builder.HistoricalAccessRPCs),
+				CollectionRPC:         builder.CollectionRPC,        // might be nil
+				HistoricalAccessNodes: builder.HistoricalAccessRPCs, // might be nil
 				Blocks:                node.Storage.Blocks,
 				Headers:               node.Storage.Headers,
 				Collections:           utils.NotNil(builder.collections),
@@ -2375,7 +2375,7 @@ func (builder *FlowAccessNodeBuilder) Build() (cmd.Node, error) {
 				utils.NotNil(builder.CollectionIndexer),
 				utils.NotNil(builder.collectionExecutedMetric),
 				builder.AccessMetrics,
-				utils.NotNil(builder.TxResultErrorMessagesCore),
+				builder.TxResultErrorMessagesCore, // will be nil if `storeTxResultErrorMessages` is false
 				builder.FollowerDistributor,
 			)
 			if err != nil {
```

### module/state_synchronization/indexer/extended/extended_indexer.go
```diff
@@ -40,11 +40,11 @@ type ExtendedIndexer struct {
 	log           zerolog.Logger
 	db            storage.DB
 	lockManager   storage.LockManager
-	state         protocol.State
 	metrics       module.ExtendedIndexingMetrics
 	backfillDelay time.Duration
 
 	chainID           flow.ChainID
+	state             protocol.State
 	blocks            storage.Blocks
 	collections       storage.Collections
 	events            storage.Events
@@ -169,6 +169,10 @@ func (c *ExtendedIndexer) IndexBlockData(
 	return nil
 }
 
+// ingestLoop is the main ingestion loop for the extended indexer.
+// It indexes the next heights for all indexers, and handles backfilling from storage.
+//
+// NOT CONCURRENCY SAFE! Only one instance may be run at a time.
 func (c *ExtendedIndexer) ingestLoop(ctx irrecoverable.SignalerContext, ready component.ReadyFunc) {
 	ready()
 
@@ -187,6 +191,8 @@ func (c *ExtendedIndexer) ingestLoop(ctx irrecoverable.SignalerContext, ready co
 			return
 		}
 
+		// once all indexers are caught up with the live height, stop resetting the backfill timer
+		// so the only notification will be for new live blocks.
 		if c.hasBackfillingIndexers() {
 			timer.Reset(c.backfillDelay)
 		}
```

### module/state_synchronization/indexer/indexer_core.go
```diff
@@ -44,7 +44,7 @@ type IndexerCore struct {
 	scheduledTransactions storage.ScheduledTransactions
 	protocolDB            storage.DB
 
-	extendedIndexer extended.IndexerManager
+	extendedIndexer *extended.ExtendedIndexer
 
 	derivedChainData *derived.DerivedChainData
 	serviceAddress   flow.Address
@@ -70,7 +70,7 @@ func New(
 	collectionIndexer collections.CollectionIndexer,
 	collectionExecutedMetric module.CollectionExecutedMetric,
 	lockManager lockctx.Manager,
-	extendedIndexer extended.IndexerManager,
+	extendedIndexer *extended.ExtendedIndexer,
 ) *IndexerCore {
 	log = log.With().Str("component", "execution_indexer").Logger()
 	metrics.InitializeLatestHeight(registers.LatestHeight())
```
