# [?] Fix panic in EthGetCode

## Summary
Severity: Unknown
Chain: Filecoin
Component: filecoin-project/lotus
Published: 2023-01-26
Source: https://github.com/filecoin-project/lotus/commit/7586710395e3cfe2104e4c8197475cd43aef9ba4
Type: security-commit

## Details
Fix panic in EthGetCode

## Patch
### itests/eth_conformance_test.go
```diff
@@ -143,7 +143,7 @@ func TestEthOpenRPCConformance(t *testing.T) {
 		variant string // suffix applied to the test name to distinguish different variants of a method call
 		call    func(*ethAPIRaw) (json.RawMessage, error)
 	}{
-		// Simple no-argument calls first
+		// Alphabetical order
 
 		{
 			method: "eth_accounts",
@@ -160,44 +160,52 @@ func TestEthOpenRPCConformance(t *testing.T) {
 		},
 
 		{
-			method: "eth_chainId",
+			method:  "eth_call",
+			variant: "latest",
 			call: func(a *ethAPIRaw) (json.RawMessage, error) {
-				return ethapi.EthChainId(context.Background())
+				return ethapi.EthCall(context.Background(), ethtypes.EthCall{
+					From: &senderEthAddr,
+					Data: contractBin,
+				}, "latest")
 			},
 		},
 
 		{
-			method: "eth_gasPrice",
+			method: "eth_chainId",
 			call: func(a *ethAPIRaw) (json.RawMessage, error) {
-				return ethapi.EthGasPrice(context.Background())
+				return ethapi.EthChainId(context.Background())
 			},
 		},
 
 		{
-			method: "eth_maxPriorityFeePerGas",
+			method: "eth_estimateGas",
 			call: func(a *ethAPIRaw) (json.RawMessage, error) {
-				return ethapi.EthMaxPriorityFeePerGas(context.Background())
+				return ethapi.EthEstimateGas(context.Background(), ethtypes.EthCall{
+					From: &senderEthAddr,
+					Data: contractBin,
+				})
 			},
 		},
 
 		{
-			method: "eth_newBlockFilter",
+			method: "eth_feeHistory",
 			call: func(a *ethAPIRaw) (json.RawMessage, error) {
-				return ethapi.EthNewBlockFilter(context.Background())
+				return ethapi.EthFeeHistory(context.Background(), ethtypes.EthUint64(2), "", nil)
 			},
 		},
 
 		{
-			method: "eth_newPendingTransactionFilter",
+			method: "eth_gasPrice",
 			call: func(a *ethAPIRaw) (json.RawMessage, error) {
-				return ethapi.EthNewPendingTransactionFilter(context.Background())
+				return ethapi.EthGasPrice(context.Background())
 			},
 		},
 
 		{
-			method: "eth_getTransactionReceipt",
+			method:  "eth_getBalance",
+			variant: "blocknumber",
 			call: func(a *ethAPIRaw) (json.RawMessage, error) {
-				return ethapi.EthGetTransactionReceipt(context.Background(), messageWithEvents)
+				return ethapi.EthGetBalance(context.Background(), contractEthAddr, "0x0")
 			},
 		},
 
@@ -255,30 +263,41 @@ func TestEthOpenRPCConformance(t *testing.T) {
 		},
 
 		{
-			method: "eth_getTransactionByBlockHashAndIndex",
+			method:  "eth_getCode",
+			variant: "blocknumber",
 			call: func(a *ethAPIRaw) (json.RawMessage, error) {
-				return ethapi.EthGetTransactionByBlockHashAndIndex(context.Background(), blockHashWithMessage, ethtypes.EthUint64(0))
+				return ethapi.EthGetCode(context.Background(), contractEthAddr, blockNumberWithMessage.Hex())
 			},
 		},
 
 		{
-			method: "eth_getTransactionByBlockNumberAndIndex",
+			method:  "eth_getFilterChanges",
+			variant: "pendingtransaction",
 			call: func(a *ethAPIRaw) (json.RawMessage, error) {
-				return ethapi.EthGetTransactionByBlockNumberAndIndex(context.Background(), blockNumberWithMessage, ethtypes.EthUint64(0))
+				return a.EthGetFilterChanges(ctx, pendingTransactionFilterID)
 			},
 		},
 
 		{
-			method: "eth_getTransactionByHash",
+			method:  "eth_getFilterChanges",
+			variant: "block",
 			call: func(a *ethAPIRaw) (json.RawMessage, error) {
-				return ethapi.EthGetTransactionByHash(context.Background(), &messageWithEvents)
+				return a.EthGetFilterChanges(ctx, blockFilterID)
 			},
 		},
 
 		{
-			method: "eth_sendRawTransaction",
+			method:  "eth_getFilterChanges",
+			variant: "logs",
 			call: func(a *ethAPIRaw) (json.RawMessage, error) {
-				return ethapi.EthSendRawTransaction(context.Background(), rawSignedEthTx)
+				return a.EthGetFilterChanges(ctx, logFilterID)
+			},
+		},
+
+		{
+			method: "eth_getFilterLogs",
+			call: func(a *ethAPIRaw) (json.RawMessage, error) {
+				return a.EthGetFilterLogs(ctx, logFilterID)
 			},
 		},
 
@@ -290,99 +309,87 @@ func TestEthOpenRPCConformance(t *testing.T) {
 		},
 
 		{
-			method:  "eth_getFilterChanges",
-			variant: "pendingtransaction",
+			method:  "eth_getStorageAt",
+			variant: "blocknumber",
 			call: func(a *ethAPIRaw) (json.RawMessage, error) {
-				return a.EthGetFilterChanges(ctx, pendingTransactionFilterID)
+				return ethapi.EthGetStorageAt(context.Background(), contractEthAddr, ethtypes.EthBytes{0}, "0x0")
 			},
 		},
 
 		{
-			method:  "eth_getFilterChanges",
-			variant: "block",
+			method: "eth_getTransactionByBlockHashAndIndex",
 			call: func(a *ethAPIRaw) (json.RawMessage, error) {
-				return a.EthGetFilterChanges(ctx, blockFilterID)
+				return ethapi.EthGetTransactionByBlockHashAndIndex(context.Background(), blockHashWithMessage, ethtypes.EthUint64(0))
 			},
 		},
 
 		{
-			method:  "eth_getFilterChanges",
-			variant: "logs",
+			method: "eth_getTransactionByBlockNumberAndIndex",
 			call: func(a *ethAPIRaw) (json.RawMessage, error) {
-				return a.EthGetFilterChanges(ctx, logFilterID)
+				return ethapi.EthGetTransactionByBlockNumberAndIndex(context.Background(), blockNumberWithMessage, ethtypes.EthUint64(0))
 			},
 		},
 
 		{
-			method: "eth_getFilterLogs",
+			method: "eth_getTransactionByHash",
 			call: func(a *ethAPIRaw) (json.RawMessage, error) {
-				return a.EthGetFilterLogs(ctx, logFilterID)
+				return ethapi.EthGetTransactionByHash(context.Background(), &messageWithEvents)
 			},
 		},
 
 		{
-			method: "eth_uninstallFilter",
+			method:  "eth_getTransactionCount",
+			variant: "blocknumber",
 			call: func(a *ethAPIRaw) (json.RawMessage, error) {
-				return a.EthUninstallFilter(ctx, uninstallableFilterID)
+				return ethapi.EthGetTransactionCount(context.Background(), senderEthAddr, blockNumberWithMessage.Hex())
 			},
 		},
 
 		{
-			method:  "eth_call",
-			variant: "latest",
+			method: "eth_getTransactionReceipt",
 			call: func(a *ethAPIRaw) (json.RawMessage, error) {
-				return ethapi.EthCall(context.Background(), ethtypes.EthCall{
-					From: &senderEthAddr,
-					Data: contractBin,
-				}, "latest")
+				return ethapi.EthGetTransactionReceipt(context.Background(), messageWithEvents)
 			},
 		},
 
 		{
-			method: "eth_estimateGas",
+			method: "eth_maxPriorityFeePerGas",
 			call: func(a *ethAPIRaw) (json.RawMessage, error) {
-				return ethapi.EthEstimateGas(context.Background(), ethtypes.EthCall{
-					From: &senderEthAddr,
-					Data: contractBin,
-				})
+				return ethapi.EthMaxPriorityFeePerGas(context.Background())
 			},
 		},
 
 		{
-			method: "eth_feeHistory",
+			method: "eth_newBlockFilter",
 			call: func(a *ethAPIRaw) (json.RawMessage, error) {
-				return ethapi.EthFeeHistory(context.Background(), ethtypes.EthUint64(2), "", nil)
+				return ethapi.EthNewBlockFilter(context.Background())
 			},
 		},
+
 		{
-			method:  "eth_getTransactionCount",
-			variant: "blocknumber",
+			method: "eth_newFilter",
 			call: func(a *ethAPIRaw) (json.RawMessage, error) {
-				return ethapi.EthGetTransactionCount(context.Background(), senderEthAddr, "0x0")
+				return ethapi.EthNewFilter(context.Background(), filterAllLogs)
 			},
 		},
 
 		{
-			method:  "eth_getCode",
-			variant: "blocknumber",
+			method: "eth_newPendingTransactionFilter",
 			call: func(a *ethAPIRaw) (json.RawMessage, error) {
-				return ethapi.EthGetCode(context.Background(), contractEthAddr, "0x0")
+				return ethapi.EthNewPendingTransactionFilter(context.Background())
 			},
 		},
 
 		{
-			method:  "eth_getStorageAt",
-			variant: "blocknumber",
+			method: "eth_sendRawTransaction",
 			call: func(a *ethAPIRaw) (json.RawMessage, error) {
-				return ethapi.EthGetStorageAt(context.Background(), contractEthAddr, ethtypes.EthBytes{0}, "0x0")
+				return ethapi.EthSendRawTransaction(context.Background(), rawSignedEthTx)
 			},
 		},
-
 		{
-			method:  "eth_getBalance",
-			variant: "blocknumber",
+			method: "eth_uninstallFilter",
 			call: func(a *ethAPIRaw) (json.RawMessage, error) {
-				return ethapi.EthGetBalance(context.Background(), contractEthAddr, "0x0")
+				return a.EthUninstallFilter(ctx, uninstallableFilterID)
 			},
 		},
 	}
```

### node/impl/full/eth.go
```diff
@@ -441,6 +441,11 @@ func (a *EthModule) EthGetCode(ctx context.Context, ethAddr ethtypes.EthAddress,
 		return nil, xerrors.Errorf("cannot parse block param: %s", blkParam)
 	}
 
+	// StateManager.Call will panic if there is no parent
+	if ts.Height() == 0 {
+		return nil, xerrors.Errorf("block param must not specify genesis block")
+	}
+
 	// Try calling until we find a height with no migration.
 	var res *api.InvocResult
 	for {
@@ -838,7 +843,6 @@ func (a *EthModule) EthCall(ctx context.Context, tx ethtypes.EthCall, blkParam s
 	if msg.To == builtintypes.EthereumAddressManagerActorAddr {
 		// As far as I can tell, the Eth API always returns empty on contract deployment
 		return ethtypes.EthBytes{}, nil
-
 	} else if len(invokeResult.MsgRct.Return) > 0 {
 		return cbg.ReadByteArray(bytes.NewReader(invokeResult.MsgRct.Return), uint64(len(invokeResult.MsgRct.Return)))
 	}
```
