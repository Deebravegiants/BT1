# [?] Prevent panic in TransactionByHash for non-existent transactions (#2373)

## Summary
Severity: Unknown
Chain: Starknet
Component: NethermindEth/juno
Published: 2025-01-14
Source: https://github.com/NethermindEth/juno/commit/0239e7780ab39c381ff95810ce1e370e0c5f4786
Type: security-commit

## Details
Prevent panic in TransactionByHash for non-existent transactions (#2373)

Fixes an issue where the code could panic when attempting to adapt a nil transaction in the pending block. This ensures the function gracefully handles non-existent transactions by returning ErrTxnHashNotFound.

## Patch
### rpc/transaction.go
```diff
@@ -440,8 +440,13 @@ func (h *Handler) TransactionByHash(hash felt.Felt) (*Transaction, *jsonrpc.Erro
 		for _, t := range pendingB.Transactions {
 			if hash.Equal(t.Hash()) {
 				txn = t
+				break
 			}
 		}
+
+		if txn == nil {
+			return nil, ErrTxnHashNotFound
+		}
 	}
 	return AdaptTransaction(txn), nil
 }
```

### rpc/transaction_test.go
```diff
@@ -39,6 +39,32 @@ func TestTransactionByHashNotFound(t *testing.T) {
 	assert.Equal(t, rpc.ErrTxnHashNotFound, rpcErr)
 }
 
+func TestTransactionByHashNotFoundInPendingBlock(t *testing.T) {
+	mockCtrl := gomock.NewController(t)
+	t.Cleanup(mockCtrl.Finish)
+	mockReader := mocks.NewMockReader(mockCtrl)
+	mockSyncReader := mocks.NewMockSyncReader(mockCtrl)
+
+	searchTxHash := utils.HexToFelt(t, "0x123456")
+
+	otherTxHash := utils.HexToFelt(t, "0x789abc")
+	pendingTx := &core.InvokeTransaction{
+		TransactionHash: otherTxHash,
+		Version:         new(core.TransactionVersion).SetUint64(1),
+	}
+
+	mockReader.EXPECT().TransactionByHash(searchTxHash).Return(nil, db.ErrKeyNotFound)
+	mockSyncReader.EXPECT().PendingBlock().Return(&core.Block{
+		Transactions: []core.Transaction{pendingTx},
+	})
+
+	handler := rpc.New(mockReader, mockSyncReader, nil, "", nil)
+
+	tx, rpcErr := handler.TransactionByHash(*searchTxHash)
+	assert.Nil(t, tx)
+	assert.Equal(t, rpc.ErrTxnHashNotFound, rpcErr)
+}
+
 func TestTransactionByHash(t *testing.T) {
 	tests := map[string]struct {
 		hash     string
```
