# [?] [Access] Fix race condition with block collection indexing

## Summary
Severity: Unknown
Chain: Flow
Component: onflow/flow-go
Published: 2026-01-30
Source: https://github.com/onflow/flow-go/commit/9e7547df568a707a3f2d7fc7be240a3b924d84c4
Type: security-commit

## Details
[Access] Fix race condition with block collection indexing

## Patch
### engine/access/rpc/backend/transactions/transactions.go
```diff
@@ -413,8 +413,13 @@ func (t *Transactions) lookupSubmittedTransactionResult(
 	// 2. lookup the block containing the collection.
 	block, err := t.blocks.ByCollectionID(collectionID)
 	if err != nil {
-		// this is an exception. the block/collection index must exist if the collection/tx is indexed,
-		// otherwise the stored state is inconsistent.
+		// it's possible (although unlikely) that the collection was synced and indexed before the
+		// ingestion engine completed indexing data for the finalized block.
+		if errors.Is(err, storage.ErrNotFound) {
+			return nil, nil, status.Errorf(codes.NotFound, "block not found for collection %v", collectionID)
+		}
+
+		// any other error is an exception.
 		err = fmt.Errorf("failed to find block for collection %v: %w", collectionID, err)
 		irrecoverable.Throw(ctx, err)
 		return nil, nil, err
```

### engine/access/rpc/backend/transactions/transactions_test.go
```diff
@@ -990,7 +990,7 @@ func (suite *Suite) TestGetTransactionResult_SubmittedTx() {
 		suite.Require().Nil(res)
 	})
 
-	suite.Run("block lookup failure throws exception", func() {
+	suite.Run("block lookup notfound returns not found error", func() {
 		suite.collections.
 			On("LightByTransactionID", txID).
 			Return(lightCollection, nil).
@@ -1007,7 +1007,34 @@ func (suite *Suite) TestGetTransactionResult_SubmittedTx() {
 		txBackend, err := NewTransactionsBackend(params)
 		suite.Require().NoError(err)
 
-		expectedErr := fmt.Errorf("failed to find block for collection %v: %w", collectionID, storage.ErrNotFound)
+		ctx := irrecoverable.NewMockSignalerContext(suite.T(), context.Background())
+		signalerCtx := irrecoverable.WithSignalerContext(context.Background(), ctx)
+
+		res, err := txBackend.GetTransactionResult(signalerCtx, txID, blockID, collectionID, encodingVersion)
+		suite.Require().Error(err)
+		suite.Require().Equal(codes.NotFound, status.Code(err))
+		suite.Require().Nil(res)
+	})
+
+	suite.Run("block lookup failure throws exception", func() {
+		suite.collections.
+			On("LightByTransactionID", txID).
+			Return(lightCollection, nil).
+			Once()
+
+		blockLookupException := fmt.Errorf("collection lookup exception")
+		suite.blocks.
+			On("ByCollectionID", collectionID).
+			Return(nil, blockLookupException).
+			Once()
+
+		params := suite.defaultTransactionsParams()
+		params.TxProvider = providermock.NewTransactionProvider(suite.T())
+
+		txBackend, err := NewTransactionsBackend(params)
+		suite.Require().NoError(err)
+
+		expectedErr := fmt.Errorf("failed to find block for collection %v: %w", collectionID, blockLookupException)
 		ctx := irrecoverable.NewMockSignalerContextExpectError(suite.T(), context.Background(), expectedErr)
 		signalerCtx := irrecoverable.WithSignalerContext(context.Background(), ctx)
 
```
