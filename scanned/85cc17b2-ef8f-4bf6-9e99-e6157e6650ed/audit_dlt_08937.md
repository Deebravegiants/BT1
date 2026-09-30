# [?] fix(vald): panic instead of stalling when no new blocks arrive (#1846)

## Summary
Severity: Unknown
Chain: Axelar
Component: axelarnetwork/axelar-core
Published: 2022-12-06
Source: https://github.com/axelarnetwork/axelar-core/commit/455c54a64abe05f736671d39a9360be3f1f92dbc
Type: security-commit

## Details
fix(vald): panic instead of stalling when no new blocks arrive (#1846)

## Patch
### vald/config/config.go
```diff
@@ -18,7 +18,8 @@ type ValdConfig struct {
 	MaxBlocksBehindLatest        int64         `mapstructure:"max_blocks_behind_latest"` // The max amount of blocks behind the latest until which the cached height is considered valid.
 	EventNotificationsMaxRetries int           `mapstructure:"event_notifications_max_retries"`
 	EventNotificationsBackOff    time.Duration `mapstructure:"event_notifications_back_off"`
-	MaxLatestBlockAge            time.Duration `mapstructure:"max_latest_block_age"` // If a block is older than this, vald does not consider it to be the latest block. This is supposed to be sufficiently larger than the block production time.
+	MaxLatestBlockAge            time.Duration `mapstructure:"max_latest_block_age"`  // If a block is older than this, vald does not consider it to be the latest block. This is supposed to be sufficiently larger than the block production time.
+	NoNewBlockPanicTimeout       time.Duration `mapstructure:"no_new_blocks_timeout"` // At times vald stalls completely. Until the bug is found it is better to panic and allow users to restart the process instead of doing nothing. Once at least one block has been seen vald will panic if it does not see another before the timout expires.
 
 	EVMConfig []evm.EVMConfig `mapstructure:"axelar_bridge_evm"`
 }
@@ -35,6 +36,7 @@ func DefaultValdConfig() ValdConfig {
 		EVMConfig:                    evm.DefaultConfig(),
 		EventNotificationsMaxRetries: 3,
 		EventNotificationsBackOff:    1 * time.Second,
+		NoNewBlockPanicTimeout:       2 * time.Minute,
 	}
 }
 
```

### vald/start.go
```diff
@@ -202,7 +202,7 @@ func listen(clientCtx sdkClient.Context, txf tx.Factory, axelarCfg config.ValdCo
 	evmMgr := createEVMMgr(axelarCfg, clientCtx, bc, logger, cdc, valAddr)
 	multisigMgr := createMultisigMgr(bc, clientCtx, axelarCfg, logger, valAddr)
 
-	nodeHeight, err := waitTillNetworkSync(axelarCfg, robustClient, logger)
+	nodeHeight, err := waitUntilNetworkSync(axelarCfg, robustClient, logger)
 	if err != nil {
 		panic(err)
 	}
@@ -214,14 +214,6 @@ func listen(clientCtx sdkClient.Context, txf tx.Factory, axelarCfg config.ValdCo
 	}
 
 	eventBus := createEventBus(robustClient, startBlock, axelarCfg.EventNotificationsMaxRetries, axelarCfg.EventNotificationsBackOff, logger)
-	subscribe := func(eventType, module, action string) <-chan tmEvents.ABCIEventWithHeight {
-		return eventBus.Subscribe(func(e tmEvents.ABCIEventWithHeight) bool {
-			event := tmEvents.Map(e)
-
-			return event.Type == eventType && event.Attributes[sdk.AttributeKeyModule] == module && event.Attributes[sdk.AttributeKeyAction] == action
-		})
-	}
-
 	var blockHeight int64
 	blockHeaderSub := eventBus.Subscribe(func(event tmEvents.ABCIEventWithHeight) bool {
 		if event.Height != blockHeight {
@@ -231,7 +223,12 @@ func listen(clientCtx sdkClient.Context, txf tx.Factory, axelarCfg config.ValdCo
 		return false
 	})
 
-	heartbeat := subscribe(tssTypes.EventTypeHeartBeat, tssTypes.ModuleName, tssTypes.AttributeValueSend)
+	heartbeat := eventBus.Subscribe(func(e tmEvents.ABCIEventWithHeight) bool {
+		event := tmEvents.Map(e)
+		return event.Type == tssTypes.EventTypeHeartBeat &&
+			event.Attributes[sdk.AttributeKeyModule] == tssTypes.ModuleName &&
+			event.Attributes[sdk.AttributeKeyAction] == tssTypes.AttributeValueSend
+	})
 
 	evmNewChain := eventBus.Subscribe(tmEvents.Filter[*evmTypes.ChainAdded]())
 	evmDepConf := eventBus.Subscribe(tmEvents.Filter[*evmTypes.ConfirmDepositStarted]())
@@ -269,7 +266,13 @@ func listen(clientCtx sdkClient.Context, txf tx.Factory, axelarCfg config.ValdCo
 		}
 	}
 
+	timer := time.AfterFunc(0, func() {})
+	defer timer.Stop()
+	blockTimeout, timeoutCancel := context.WithCancel(context.Background())
 	processBlockHeader := func(event tmEvents.Event) error {
+		timer.Stop()
+		timer = time.AfterFunc(axelarCfg.NoNewBlockPanicTimeout, timeoutCancel)
+
 		return stateStore.SetState(event.Height)
 	}
 
@@ -287,7 +290,12 @@ func listen(clientCtx sdkClient.Context, txf tx.Factory, axelarCfg config.ValdCo
 	}
 
 	mgr.AddJobs(js...)
-	<-mgr.Done()
+	select {
+	case <-mgr.Done():
+		return
+	case <-blockTimeout.Done():
+		panic("no new blocks received from the node")
+	}
 }
 
 func createJob(sub <-chan tmEvents.ABCIEventWithHeight, processor func(event tmEvents.Event) error, cancel context.CancelFunc, logger log.Logger) jobs.Job {
@@ -330,7 +338,7 @@ func createJobTyped[T proto.Message](sub <-chan tmEvents.ABCIEventWithHeight, pr
 }
 
 // Wait until the node has synced with the network and return the node height
-func waitTillNetworkSync(cfg config.ValdConfig, tmClient tmEvents.SyncInfoClient, logger log.Logger) (int64, error) {
+func waitUntilNetworkSync(cfg config.ValdConfig, tmClient tmEvents.SyncInfoClient, logger log.Logger) (int64, error) {
 	for {
 		rpcCtx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
 		syncInfo, err := tmClient.LatestSyncInfo(rpcCtx)
```

### vald/start_test.go
```diff
@@ -0,0 +1,45 @@
+package vald
+
+import (
+	"context"
+	"testing"
+	"time"
+
+	"github.com/stretchr/testify/assert"
+)
+
+// proof of concept for the panic mechanism used in the listen(...) function to panic when it takes too long to see new blocks
+func TestPanic(t *testing.T) {
+	testTimeout, testCancel := context.WithTimeout(context.Background(), 1*time.Second)
+	defer testCancel()
+
+	assert.Panics(t, func() {
+		timer := time.AfterFunc(0, func() {})
+		defer timer.Stop()
+		blockTimeout, timeoutCancel := context.WithCancel(context.Background())
+		blocksSeen := 0
+		newBlock := func() {
+			timer.Stop()
+			timer = time.AfterFunc(1*time.Millisecond, func() {
+				timeoutCancel()
+			})
+			blocksSeen++
+		}
+
+		go func() {
+			for i := 0; i < 1000; i++ {
+				newBlock()
+			}
+			time.Sleep(2 * time.Millisecond)
+			newBlock()
+		}()
+
+		select {
+		case <-testTimeout.Done():
+			return
+		case <-blockTimeout.Done():
+			assert.Equal(t, 1000, blocksSeen)
+			panic("no new blocks discovered, is the chain halted?")
+		}
+	})
+}
```
