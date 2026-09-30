# [?] fix max big int limit comparison issue with overflow

## Summary
Severity: Unknown
Chain: Harmony
Component: harmony-one/harmony
Published: 2019-08-09
Source: https://github.com/harmony-one/harmony/commit/7d912809671d59c8acb164b3a59e0fa159a284ff
Type: security-commit

## Details
fix max big int limit comparison issue with overflow

## Patch
### internal/configs/sharding/fixedschedule.go
```diff
@@ -34,8 +34,8 @@ func (s fixedSchedule) IsLastBlock(blockNum uint64) bool {
 	return blockNum%blocks == blocks-1
 }
 
-func (s fixedSchedule) MaxTxAmountLimit() *big.Int {
-	amountBigInt := big.NewInt(int64(mainnetMaxTxAmountLimit * denominations.Nano))
+func (s fixedSchedule) MaxTxAmountNanoLimit() *big.Int {
+	amountBigInt := big.NewInt(mainnetMaxTxAmountNanoLimit)
 	amountBigInt = amountBigInt.Mul(amountBigInt, big.NewInt(denominations.Nano))
 	return amountBigInt
 }
@@ -50,7 +50,7 @@ func (s fixedSchedule) MaxTxsPerBlockLimit() int {
 
 func (s fixedSchedule) TxsThrottleConfig() *TxsThrottleConfig {
 	return &TxsThrottleConfig{
-		MaxTxAmountLimit:               s.MaxTxAmountLimit(),
+		MaxTxAmountNanoLimit:           s.MaxTxAmountNanoLimit(),
 		MaxNumRecentTxsPerAccountLimit: s.MaxNumRecentTxsPerAccountLimit(),
 		MaxTxsPerBlockLimit:            s.MaxTxsPerBlockLimit(),
 	}
```

### internal/configs/sharding/localnet.go
```diff
@@ -20,7 +20,7 @@ const (
 	localnetEpochBlock1 = 20
 	twoOne              = 5
 
-	localnetMaxTxAmountLimit               = 1e2 // unit is in One
+	localnetMaxTxAmountNanoLimit           = 1e2 // unit is in One
 	localnetMaxNumRecentTxsPerAccountLimit = 2
 	localnetMaxTxsPerBlockLimit            = 8000
 )
@@ -62,8 +62,8 @@ func (ls localnetSchedule) IsLastBlock(blockNum uint64) bool {
 	}
 }
 
-func (ls localnetSchedule) MaxTxAmountLimit() *big.Int {
-	amountBigInt := big.NewInt(int64(localnetMaxTxAmountLimit * denominations.Nano))
+func (ls localnetSchedule) MaxTxAmountNanoLimit() *big.Int {
+	amountBigInt := big.NewInt(localnetMaxTxAmountNanoLimit)
 	amountBigInt = amountBigInt.Mul(amountBigInt, big.NewInt(denominations.Nano))
 	return amountBigInt
 }
@@ -78,7 +78,7 @@ func (ls localnetSchedule) MaxTxsPerBlockLimit() int {
 
 func (ls localnetSchedule) TxsThrottleConfig() *TxsThrottleConfig {
 	return &TxsThrottleConfig{
-		MaxTxAmountLimit:               ls.MaxTxAmountLimit(),
+		MaxTxAmountNanoLimit:           ls.MaxTxAmountNanoLimit(),
 		MaxNumRecentTxsPerAccountLimit: ls.MaxNumRecentTxsPerAccountLimit(),
 		MaxTxsPerBlockLimit:            ls.MaxTxsPerBlockLimit(),
 	}
```

### internal/configs/sharding/mainnet.go
```diff
@@ -16,7 +16,7 @@ const (
 	mainnetV0_3Epoch   = 8
 	mainnetV0_4Epoch   = 10
 
-	mainnetMaxTxAmountLimit               = 1e3 // unit is in One
+	mainnetMaxTxAmountNanoLimit           = 1e3 // unit is in One
 	mainnetMaxNumRecentTxsPerAccountLimit = 10
 	mainnetMaxTxsPerBlockLimit            = 8000
 )
@@ -71,8 +71,8 @@ func (ms mainnetSchedule) IsLastBlock(blockNum uint64) bool {
 	}
 }
 
-func (ms mainnetSchedule) MaxTxAmountLimit() *big.Int {
-	amountBigInt := big.NewInt(int64(mainnetMaxTxAmountLimit * denominations.Nano))
+func (ms mainnetSchedule) MaxTxAmountNanoLimit() *big.Int {
+	amountBigInt := big.NewInt(mainnetMaxTxAmountNanoLimit)
 	amountBigInt = amountBigInt.Mul(amountBigInt, big.NewInt(denominations.Nano))
 	return amountBigInt
 }
@@ -87,7 +87,7 @@ func (ms mainnetSchedule) MaxTxsPerBlockLimit() int {
 
 func (ms mainnetSchedule) TxsThrottleConfig() *TxsThrottleConfig {
 	return &TxsThrottleConfig{
-		MaxTxAmountLimit:               ms.MaxTxAmountLimit(),
+		MaxTxAmountNanoLimit:           ms.MaxTxAmountNanoLimit(),
 		MaxNumRecentTxsPerAccountLimit: ms.MaxNumRecentTxsPerAccountLimit(),
 		MaxTxsPerBlockLimit:            ms.MaxTxsPerBlockLimit(),
 	}
```

### internal/configs/sharding/shardingconfig.go
```diff
@@ -23,7 +23,7 @@ type Schedule interface {
 	IsLastBlock(blockNum uint64) bool
 
 	// Max amount limit for a valid transaction
-	MaxTxAmountLimit() *big.Int
+	MaxTxAmountNanoLimit() *big.Int
 
 	// Max number of transactions of a particular account per block level
 	MaxNumRecentTxsPerAccountLimit() uint64
@@ -85,7 +85,7 @@ func (result TxThrottleFlag) String() string {
 // TxsThrottleConfig contains configuration for throttling pending transactions per node block
 type TxsThrottleConfig struct {
 	// Max amount limit for a valid transaction
-	MaxTxAmountLimit *big.Int
+	MaxTxAmountNanoLimit *big.Int
 
 	// Max number of transactions of a particular account for the past hour
 	MaxNumRecentTxsPerAccountLimit uint64
```

### internal/configs/sharding/testnet.go
```diff
@@ -20,7 +20,7 @@ const (
 	testnetEpochBlock1 = 78
 	threeOne           = 111
 
-	testnetMaxTxAmountLimit               = 1e3 // unit is in One
+	testnetMaxTxAmountNanoLimit           = 1e3 // unit is in One
 	testnetMaxNumRecentTxsPerAccountLimit = 10
 	testnetMaxTxsPerBlockLimit            = 8000
 )
@@ -63,8 +63,8 @@ func (ts testnetSchedule) IsLastBlock(blockNum uint64) bool {
 	}
 }
 
-func (ts testnetSchedule) MaxTxAmountLimit() *big.Int {
-	amountBigInt := big.NewInt(int64(testnetMaxTxAmountLimit * denominations.Nano))
+func (ts testnetSchedule) MaxTxAmountNanoLimit() *big.Int {
+	amountBigInt := big.NewInt(testnetMaxTxAmountNanoLimit)
 	amountBigInt = amountBigInt.Mul(amountBigInt, big.NewInt(denominations.Nano))
 	return amountBigInt
 }
@@ -79,7 +79,7 @@ func (ts testnetSchedule) MaxTxsPerBlockLimit() int {
 
 func (ts testnetSchedule) TxsThrottleConfig() *TxsThrottleConfig {
 	return &TxsThrottleConfig{
-		MaxTxAmountLimit:               ts.MaxTxAmountLimit(),
+		MaxTxAmountNanoLimit:           ts.MaxTxAmountNanoLimit(),
 		MaxNumRecentTxsPerAccountLimit: ts.MaxNumRecentTxsPerAccountLimit(),
 		MaxTxsPerBlockLimit:            ts.MaxTxsPerBlockLimit(),
 	}
```

### node/node.go
```diff
@@ -271,8 +271,7 @@ func (node *Node) getTransactionsForNewBlock(coinbase common.Address) types.Tran
 	node.pendingTransactions = unselected
 	node.reducePendingTransactions()
 
-	utils.GetLogInstance().Info(
-		"msg", "Selecting Transactions",
+	utils.GetLogInstance().Info("Selecting Transactions",
 		"newBlockNum", newBlockNum,
 		"remainPending", len(node.pendingTransactions),
 		"invalidDiscarded", len(invalid))
@@ -506,17 +505,17 @@ func (node *Node) initNodeConfiguration() (service.NodeConfig, chan p2p.Peer) {
 	var err error
 	node.shardGroupReceiver, err = node.host.GroupReceiver(node.NodeConfig.GetShardGroupID())
 	if err != nil {
-		utils.GetLogInstance().Error("Failed to create shard receiver", "msg", err)
+		utils.GetLogInstance().Error("Failed to create shard receiver", "err", err)
 	}
 
 	node.globalGroupReceiver, err = node.host.GroupReceiver(p2p.GroupIDBeaconClient)
 	if err != nil {
-		utils.GetLogInstance().Error("Failed to create global receiver", "msg", err)
+		utils.GetLogInstance().Error("Failed to create global receiver", "err", err)
 	}
 
 	node.clientReceiver, err = node.host.GroupReceiver(node.NodeConfig.GetClientGroupID())
 	if err != nil {
-		utils.GetLogInstance().Error("Failed to create client receiver", "msg", err)
+		utils.GetLogInstance().Error("Failed to create client receiver", "err", err)
 	}
 	return nodeConfig, chanPeer
 }
```

### node/worker/worker.go
```diff
@@ -59,24 +59,25 @@ func (w *Worker) throttleTxs(selected types.Transactions, recentTxsStats types.R
 	var sender common.Address
 	msg, err := tx.AsMessage(s)
 	if err != nil {
-		utils.GetLogInstance().Error("Error when parsing tx into message", "msg", err)
+		utils.GetLogInstance().Error("Error when parsing tx into message",
+			"tx Id", tx.Hash().Hex(), "err", err)
 	} else {
 		sender = msg.From()
 	}
 
 	// already selected max num txs
-	if len(selected) > (*txsThrottleConfig).MaxTxsPerBlockLimit {
-		utils.GetLogInstance().Info(
-			"msg", "Throttling tx with max txs per block limit",
+	if len(selected) > txsThrottleConfig.MaxTxsPerBlockLimit {
+		utils.GetLogInstance().Info("Throttling tx with max txs per block limit",
+			"tx Id", tx.Hash().Hex(),
 			"MaxTxsPerBlockLimit", txsThrottleConfig.MaxTxsPerBlockLimit)
 		return sender, shardingconfig.TxUnselect
 	}
 
 	// throttle a single sender sending too many transactions in one block
-	if (txsThrottleConfig.MaxTxAmountLimit).Cmp(tx.Value()) < 0 {
-		utils.GetLogInstance().Info(
-			"msg", "Throttling tx with max amount limit",
-			"MaxTxAmountLimit", txsThrottleConfig.MaxTxAmountLimit.Uint64(),
+	if txsThrottleConfig.MaxTxAmountNanoLimit.Cmp(tx.Value()) < 0 {
+		utils.GetLogInstance().Info("Throttling tx with max amount limit",
+			"tx Id", tx.Hash().Hex(),
+			"MaxTxAmountNanoLimit", txsThrottleConfig.MaxTxAmountNanoLimit.Uint64(),
 			"Tx amount", tx.Value().Uint64())
 		return sender, shardingconfig.TxInvalid
 	}
@@ -87,8 +88,8 @@ func (w *Worker) throttleTxs(selected types.Transactions, recentTxsStats types.R
 		numTxsPastHour += blockTxsCounts[sender]
 	}
 	if numTxsPastHour >= txsThrottleConfig.MaxNumRecentTxsPerAccountLimit {
-		utils.GetLogInstance().Info(
-			"msg", "Throttling tx with max txs per account in a single block limit",
+		utils.GetLogInstance().Info("Throttling tx with max txs per account in a single block limit",
+			"tx Id", tx.Hash().Hex(),
 			"MaxNumRecentTxsPerAccountLimit", txsThrottleConfig.MaxNumRecentTxsPerAccountLimit)
 		return sender, shardingconfig.TxUnselect
 	}
@@ -133,8 +134,7 @@ func (w *Worker) SelectTransactionsForNewBlock(newBlockNum uint64, txs types.Tra
 
 		// log invalid or unselected txs
 		if flag == shardingconfig.TxUnselect || flag == shardingconfig.TxInvalid {
-			utils.GetLogInstance().Info(
-				"msg", "Transaction Throttle flag",
+			utils.GetLogInstance().Info("Transaction Throttle flag",
 				"Transaction Id", tx.Hash().Hex(),
 				"txThrottleFlag", flag.String())
 		}
```
