# [?] tests: fix panic db closed in TestDump (#16135)

## Summary
Severity: Unknown
Chain: Ethereum
Component: erigontech/erigon
Published: 2025-07-22
Source: https://github.com/erigontech/erigon/commit/1ee449d8c0b62b97963d8c6212385c4ec4aceb42
Type: security-commit

## Details
tests: fix panic db closed in TestDump (#16135)

Fixes #15427 

The root cause:
- `freezeblocks.RetireBlocksInBackground` starts a goroutine doing the
retirement of blocks in background, but there's no way to wait for
completion of such goroutine
- `TestDump` contains a loop creating a test chain at each iteration
through `MockSentry` and running a staged sync iteration over it, which
triggers the retirement of blocks (even if it's a no-op). The test
database gets closed at the end of the test by `tb.Cleanup(mock.Close)`

Hence, there's an unlikely race condition between the `TestDump`
goroutine closing the db and the background retirement goroutine
accessing the db, which may be already closed.

The changes:
- add boolean return value in `RetireBlocksInBackground` to indicate if
a new background retirement task has been scheduled or not (it may be
not if a previous one is already running)
- add `onDone` callback to signal the completion of a background
retirement task
- add `retirementStartSubscription` and `retirementDoneSubscription` in
`Events` publish-subscribe bus
- subscribe `MockSentry` to receive notifications of retirement
started/completed
- register a `testing.TB.Cleanup` hook to wait for the completion of all
the background retirements actually scheduled when
`stages2.StageLoopIteration` is called in `MockSentry` (i.e. when
`MockSentry.InsertChain` is called)

## Patch
### execution/stagedsync/stage_snapshots.go
```diff
@@ -454,35 +454,46 @@ func SnapshotsPrune(s *PruneState, cfg SnapshotsCfg, ctx context.Context, tx kv.
 			cfg.blockRetire.SetWorkers(1)
 		}
 
-		cfg.blockRetire.RetireBlocksInBackground(ctx, minBlockNumber, s.ForwardProgress, log.LvlDebug, func(downloadRequest []snapshotsync.DownloadRequest) error {
-			if cfg.snapshotDownloader != nil && !reflect.ValueOf(cfg.snapshotDownloader).IsNil() {
-				if err := snapshotsync.RequestSnapshotsDownload(ctx, downloadRequest, cfg.snapshotDownloader, ""); err != nil {
-					return err
+		started := cfg.blockRetire.RetireBlocksInBackground(
+			ctx,
+			minBlockNumber,
+			s.ForwardProgress,
+			log.LvlDebug,
+			func(downloadRequest []snapshotsync.DownloadRequest) error {
+				if cfg.snapshotDownloader != nil && !reflect.ValueOf(cfg.snapshotDownloader).IsNil() {
+					if err := snapshotsync.RequestSnapshotsDownload(ctx, downloadRequest, cfg.snapshotDownloader, ""); err != nil {
+						return err
+					}
 				}
-			}
 
-			return nil
-		}, func(l []string) error {
-			//if cfg.snapshotUploader != nil {
-			// TODO - we need to also remove files from the uploader (100k->500K transition)
-			//}
+				return nil
+			}, func(l []string) error {
+				//if cfg.snapshotUploader != nil {
+				// TODO - we need to also remove files from the uploader (100k->500K transition)
+				//}
 
-			if !(cfg.snapshotDownloader == nil || reflect.ValueOf(cfg.snapshotDownloader).IsNil()) {
-				_, err := cfg.snapshotDownloader.Delete(ctx, &protodownloader.DeleteRequest{Paths: l})
-				return err
-			}
+				if !(cfg.snapshotDownloader == nil || reflect.ValueOf(cfg.snapshotDownloader).IsNil()) {
+					_, err := cfg.snapshotDownloader.Delete(ctx, &protodownloader.DeleteRequest{Paths: l})
+					return err
+				}
 
-			return nil
-		}, func() error {
-			filesDeleted, err := pruneBlockSnapshots(ctx, cfg, logger)
-			if filesDeleted && cfg.notifier != nil {
-				cfg.notifier.Events.OnNewSnapshot()
-			}
-			return err
-		})
+				return nil
+			}, func() error {
+				filesDeleted, err := pruneBlockSnapshots(ctx, cfg, logger)
+				if filesDeleted && cfg.notifier != nil {
+					cfg.notifier.Events.OnNewSnapshot()
+				}
+				return err
+			}, func() {
+				if cfg.notifier != nil {
+					cfg.notifier.Events.OnRetirementDone()
+				}
+			})
+		if cfg.notifier != nil {
+			cfg.notifier.Events.OnRetirementStart(started)
+		}
 
 		//	cfg.agg.BuildFilesInBackground()
-
 	}
 
 	pruneLimit := 10
```

### execution/stages/mock/mock_sentry.go
```diff
@@ -119,6 +119,9 @@ type MockSentry struct {
 	ReceiveWg            sync.WaitGroup
 	Address              common.Address
 	Eth1ExecutionService *eth1.EthereumExecutionModule
+	retirementStart      chan bool
+	retirementDone       chan struct{}
+	retirementWg         sync.WaitGroup
 
 	Notifications *shards.Notifications
 
@@ -318,9 +321,15 @@ func MockWithEverything(tb testing.TB, gspec *types.Genesis, key *ecdsa.PrivateK
 		HistoryV3:      true,
 		cfg:            cfg,
 	}
+	mock.retirementStart, _ = mock.Notifications.Events.AddRetirementStartSubscription()
+	mock.retirementDone, _ = mock.Notifications.Events.AddRetirementDoneSubscription()
 
 	if tb != nil {
 		tb.Cleanup(mock.Close)
+		tb.Cleanup(func() {
+			// Wait for all the background snapshot retirements launched by any stages2.StageLoopIteration to finish
+			mock.retirementWg.Wait()
+		})
 	}
 
 	// Committed genesis will be shared between download and mock sentry
@@ -789,6 +798,15 @@ func (ms *MockSentry) insertPoWBlocks(chain *core.ChainPack) error {
 	if err = stages2.StageLoopIteration(ms.Ctx, ms.DB, wrap.NewTxContainer(nil, nil), ms.Sync, initialCycle, firstCycle, ms.Log, ms.BlockReader, hook); err != nil {
 		return err
 	}
+	// Wait to know if a new background retirement has started
+	if retirementStarted := <-ms.retirementStart; retirementStarted {
+		// If so, increment the background retirement counter and start a task to watch for its completion
+		ms.retirementWg.Add(1)
+		go func() {
+			defer ms.retirementWg.Done()
+			<-ms.retirementDone
+		}()
+	}
 	if ms.TxPool != nil {
 		ms.ReceiveWg.Wait() // Wait for TxPool notification
 	}
```

### turbo/services/interfaces.go
```diff
@@ -149,7 +149,15 @@ type FullBlockReader interface {
 // BlockRetire - freezing blocks: moving old data from DB to snapshot files
 type BlockRetire interface {
 	PruneAncientBlocks(tx kv.RwTx, limit int, timeout time.Duration) (deleted int, err error)
-	RetireBlocksInBackground(ctx context.Context, miBlockNum uint64, maxBlockNum uint64, lvl log.Lvl, seedNewSnapshots func(downloadRequest []snapshotsync.DownloadRequest) error, onDelete func(l []string) error, onFinishRetire func() error)
+	RetireBlocksInBackground(
+		ctx context.Context,
+		miBlockNum uint64,
+		maxBlockNum uint64,
+		lvl log.Lvl,
+		seedNewSnapshots func(downloadRequest []snapshotsync.DownloadRequest) error,
+		onDelete func(l []string) error,
+		onFinishRetire func() error,
+		onDone func()) bool
 	BuildMissedIndicesIfNeed(ctx context.Context, logPrefix string, notifier DBEventNotifier) error
 	SetWorkers(workers int)
 	GetWorkers() int
```

### turbo/shards/events.go
```diff
@@ -38,25 +38,29 @@ type LogsSubscription func([]*remote.SubscribeLogsReply) error
 
 // Events manages event subscriptions and dissimination. Thread-safe
 type Events struct {
-	id                        int
-	headerSubscriptions       map[int]chan [][]byte
-	newSnapshotSubscription   map[int]chan struct{}
-	pendingLogsSubscriptions  map[int]PendingLogsSubscription
-	pendingBlockSubscriptions map[int]PendingBlockSubscription
-	pendingTxsSubscriptions   map[int]PendingTxsSubscription
-	logsSubscriptions         map[int]chan []*remote.SubscribeLogsReply
-	hasLogSubscriptions       bool
-	lock                      sync.RWMutex
+	id                          int
+	headerSubscriptions         map[int]chan [][]byte
+	newSnapshotSubscription     map[int]chan struct{}
+	retirementStartSubscription map[int]chan bool
+	retirementDoneSubscription  map[int]chan struct{}
+	pendingLogsSubscriptions    map[int]PendingLogsSubscription
+	pendingBlockSubscriptions   map[int]PendingBlockSubscription
+	pendingTxsSubscriptions     map[int]PendingTxsSubscription
+	logsSubscriptions           map[int]chan []*remote.SubscribeLogsReply
+	hasLogSubscriptions         bool
+	lock                        sync.RWMutex
 }
 
 func NewEvents() *Events {
 	return &Events{
-		headerSubscriptions:       map[int]chan [][]byte{},
-		pendingLogsSubscriptions:  map[int]PendingLogsSubscription{},
-		pendingBlockSubscriptions: map[int]PendingBlockSubscription{},
-		pendingTxsSubscriptions:   map[int]PendingTxsSubscription{},
-		logsSubscriptions:         map[int]chan []*remote.SubscribeLogsReply{},
-		newSnapshotSubscription:   map[int]chan struct{}{},
+		headerSubscriptions:         map[int]chan [][]byte{},
+		pendingLogsSubscriptions:    map[int]PendingLogsSubscription{},
+		pendingBlockSubscriptions:   map[int]PendingBlockSubscription{},
+		pendingTxsSubscriptions:     map[int]PendingTxsSubscription{},
+		logsSubscriptions:           map[int]chan []*remote.SubscribeLogsReply{},
+		newSnapshotSubscription:     map[int]chan struct{}{},
+		retirementStartSubscription: map[int]chan bool{},
+		retirementDoneSubscription:  map[int]chan struct{}{},
 	}
 }
 
@@ -86,6 +90,32 @@ func (e *Events) AddNewSnapshotSubscription() (chan struct{}, func()) {
 	}
 }
 
+func (e *Events) AddRetirementStartSubscription() (chan bool, func()) {
+	e.lock.Lock()
+	defer e.lock.Unlock()
+	ch := make(chan bool, 8)
+	e.id++
+	id := e.id
+	e.retirementStartSubscription[id] = ch
+	return ch, func() {
+		delete(e.retirementStartSubscription, id)
+		close(ch)
+	}
+}
+
+func (e *Events) AddRetirementDoneSubscription() (chan struct{}, func()) {
+	e.lock.Lock()
+	defer e.lock.Unlock()
+	ch := make(chan struct{}, 8)
+	e.id++
+	id := e.id
+	e.retirementDoneSubscription[id] = ch
+	return ch, func() {
+		delete(e.retirementDoneSubscription, id)
+		close(ch)
+	}
+}
+
 func (e *Events) AddLogsSubscription() (chan []*remote.SubscribeLogsReply, func()) {
 	e.lock.Lock()
 	defer e.lock.Unlock()
@@ -157,6 +187,22 @@ func (e *Events) OnLogs(logs []*remote.SubscribeLogsReply) {
 	}
 }
 
+func (e *Events) OnRetirementStart(started bool) {
+	e.lock.Lock()
+	defer e.lock.Unlock()
+	for _, ch := range e.retirementStartSubscription {
+		common.PrioritizedSend(ch, started)
+	}
+}
+
+func (e *Events) OnRetirementDone() {
+	e.lock.Lock()
+	defer e.lock.Unlock()
+	for _, ch := range e.retirementDoneSubscription {
+		common.PrioritizedSend(ch, struct{}{})
+	}
+}
+
 type Notifications struct {
 	Events               *Events
 	Accumulator          *Accumulator // StateAccumulator
```

### turbo/snapshotsync/freezeblocks/block_snapshots.go
```diff
@@ -394,16 +394,26 @@ func (br *BlockRetire) PruneAncientBlocks(tx kv.RwTx, limit int, timeout time.Du
 	return deleted + deletedBorBlocks, nil
 }
 
-func (br *BlockRetire) RetireBlocksInBackground(ctx context.Context, minBlockNum, maxBlockNum uint64, lvl log.Lvl, seedNewSnapshots func(downloadRequest []snapshotsync.DownloadRequest) error, onDeleteSnapshots func(l []string) error, onFinishRetire func() error) {
+func (br *BlockRetire) RetireBlocksInBackground(
+	ctx context.Context,
+	minBlockNum,
+	maxBlockNum uint64,
+	lvl log.Lvl,
+	seedNewSnapshots func(downloadRequest []snapshotsync.DownloadRequest) error,
+	onDeleteSnapshots func(l []string) error,
+	onFinishRetire func() error,
+	onDone func(),
+) bool {
 	if maxBlockNum > br.maxScheduledBlock.Load() {
 		br.maxScheduledBlock.Store(maxBlockNum)
 	}
 
 	if !br.working.CompareAndSwap(false, true) {
-		return
+		return false
 	}
 
 	go func() {
+		defer onDone()
 		defer br.working.Store(false)
 
 		if br.snBuildAllowed != nil {
@@ -424,6 +434,8 @@ func (br *BlockRetire) RetireBlocksInBackground(ctx context.Context, minBlockNum
 			return
 		}
 	}()
+
+	return true
 }
 
 func (br *BlockRetire) RetireBlocks(ctx context.Context, requestedMinBlockNum uint64, requestedMaxBlockNum uint64, lvl log.Lvl, seedNewSnapshots func(downloadRequest []snapshotsync.DownloadRequest) error, onDeleteSnapshots func(l []string) error, onFinish func() error) error {
```
