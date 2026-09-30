# [?] eth/filters: fix potential deadlock in filter timeout loop (#22178)

## Summary
Severity: Unknown
Chain: Ethereum
Component: ethereum/go-ethereum
Published: 2021-01-21
Source: https://github.com/ethereum/go-ethereum/commit/c4307a9339fd4e66598fd5c378e8f6f97ad878e2
Type: security-commit

## Details
eth/filters: fix potential deadlock in filter timeout loop (#22178)

This fixes #22131 and adds a test reproducing the issue.

## Patch
### eth/backend.go
```diff
@@ -335,7 +335,7 @@ func (s *Ethereum) APIs() []rpc.API {
 		}, {
 			Namespace: "eth",
 			Version:   "1.0",
-			Service:   filters.NewPublicFilterAPI(s.APIBackend, false),
+			Service:   filters.NewPublicFilterAPI(s.APIBackend, false, 5*time.Minute),
 			Public:    true,
 		}, {
 			Namespace: "admin",
```

### eth/filters/api.go
```diff
@@ -34,10 +34,6 @@ import (
 	"github.com/ethereum/go-ethereum/rpc"
 )
 
-var (
-	deadline = 5 * time.Minute // consider a filter inactive if it has not been polled for within deadline
-)
-
 // filter is a helper struct that holds meta information over the filter type
 // and associated subscription in the event system.
 type filter struct {
@@ -59,39 +55,50 @@ type PublicFilterAPI struct {
 	events    *EventSystem
 	filtersMu sync.Mutex
 	filters   map[rpc.ID]*filter
+	timeout   time.Duration
 }
 
 // NewPublicFilterAPI returns a new PublicFilterAPI instance.
-func NewPublicFilterAPI(backend Backend, lightMode bool) *PublicFilterAPI {
+func NewPublicFilterAPI(backend Backend, lightMode bool, timeout time.Duration) *PublicFilterAPI {
 	api := &PublicFilterAPI{
 		backend: backend,
 		chainDb: backend.ChainDb(),
 		events:  NewEventSystem(backend, lightMode),
 		filters: make(map[rpc.ID]*filter),
+		timeout: timeout,
 	}
-	go api.timeoutLoop()
+	go api.timeoutLoop(timeout)
 
 	return api
 }
 
 // timeoutLoop runs every 5 minutes and deletes filters that have not been recently used.
 // Tt is started when the api is created.
-func (api *PublicFilterAPI) timeoutLoop() {
-	ticker := time.NewTicker(5 * time.Minute)
+func (api *PublicFilterAPI) timeoutLoop(timeout time.Duration) {
+	var toUninstall []*Subscription
+	ticker := time.NewTicker(timeout)
 	defer ticker.Stop()
 	for {
 		<-ticker.C
 		api.filtersMu.Lock()
 		for id, f := range api.filters {
 			select {
 			case <-f.deadline.C:
-				f.s.Unsubscribe()
+				toUninstall = append(toUninstall, f.s)
 				delete(api.filters, id)
 			default:
 				continue
 			}
 		}
 		api.filtersMu.Unlock()
+
+		// Unsubscribes are processed outside the lock to avoid the following scenario:
+		// event loop attempts broadcasting events to still active filters while
+		// Unsubscribe is waiting for it to process the uninstall request.
+		for _, s := range toUninstall {
+			s.Unsubscribe()
+		}
+		toUninstall = nil
 	}
 }
 
@@ -109,7 +116,7 @@ func (api *PublicFilterAPI) NewPendingTransactionFilter() rpc.ID {
 	)
 
 	api.filtersMu.Lock()
-	api.filters[pendingTxSub.ID] = &filter{typ: PendingTransactionsSubscription, deadline: time.NewTimer(deadline), hashes: make([]common.Hash, 0), s: pendingTxSub}
+	api.filters[pendingTxSub.ID] = &filter{typ: PendingTransactionsSubscription, deadline: time.NewTimer(api.timeout), hashes: make([]common.Hash, 0), s: pendingTxSub}
 	api.filtersMu.Unlock()
 
 	go func() {
@@ -179,7 +186,7 @@ func (api *PublicFilterAPI) NewBlockFilter() rpc.ID {
 	)
 
 	api.filtersMu.Lock()
-	api.filters[headerSub.ID] = &filter{typ: BlocksSubscription, deadline: time.NewTimer(deadline), hashes: make([]common.Hash, 0), s: headerSub}
+	api.filters[headerSub.ID] = &filter{typ: BlocksSubscription, deadline: time.NewTimer(api.timeout), hashes: make([]common.Hash, 0), s: headerSub}
 	api.filtersMu.Unlock()
 
 	go func() {
@@ -296,7 +303,7 @@ func (api *PublicFilterAPI) NewFilter(crit FilterCriteria) (rpc.ID, error) {
 	}
 
 	api.filtersMu.Lock()
-	api.filters[logsSub.ID] = &filter{typ: LogsSubscription, crit: crit, deadline: time.NewTimer(deadline), logs: make([]*types.Log, 0), s: logsSub}
+	api.filters[logsSub.ID] = &filter{typ: LogsSubscription, crit: crit, deadline: time.NewTimer(api.timeout), logs: make([]*types.Log, 0), s: logsSub}
 	api.filtersMu.Unlock()
 
 	go func() {
@@ -421,7 +428,7 @@ func (api *PublicFilterAPI) GetFilterChanges(id rpc.ID) (interface{}, error) {
 			// receive timer value and reset timer
 			<-f.deadline.C
 		}
-		f.deadline.Reset(deadline)
+		f.deadline.Reset(api.timeout)
 
 		switch f.typ {
 		case PendingTransactionsSubscription, BlocksSubscription:
```

### eth/filters/filter_system_test.go
```diff
@@ -22,6 +22,7 @@ import (
 	"math/big"
 	"math/rand"
 	"reflect"
+	"runtime"
 	"testing"
 	"time"
 
@@ -38,6 +39,10 @@ import (
 	"github.com/ethereum/go-ethereum/rpc"
 )
 
+var (
+	deadline = 5 * time.Minute
+)
+
 type testBackend struct {
 	mux             *event.TypeMux
 	db              ethdb.Database
@@ -163,7 +168,7 @@ func TestBlockSubscription(t *testing.T) {
 	var (
 		db          = rawdb.NewMemoryDatabase()
 		backend     = &testBackend{db: db}
-		api         = NewPublicFilterAPI(backend, false)
+		api         = NewPublicFilterAPI(backend, false, deadline)
 		genesis     = new(core.Genesis).MustCommit(db)
 		chain, _    = core.GenerateChain(params.TestChainConfig, genesis, ethash.NewFaker(), db, 10, func(i int, gen *core.BlockGen) {})
 		chainEvents = []core.ChainEvent{}
@@ -215,7 +220,7 @@ func TestPendingTxFilter(t *testing.T) {
 	var (
 		db      = rawdb.NewMemoryDatabase()
 		backend = &testBackend{db: db}
-		api     = NewPublicFilterAPI(backend, false)
+		api     = NewPublicFilterAPI(backend, false, deadline)
 
 		transactions = []*types.Transaction{
 			types.NewTransaction(0, common.HexToAddress("0xb794f5ea0ba39494ce83a213fffba74279579268"), new(big.Int), 0, new(big.Int), nil),
@@ -270,7 +275,7 @@ func TestLogFilterCreation(t *testing.T) {
 	var (
 		db      = rawdb.NewMemoryDatabase()
 		backend = &testBackend{db: db}
-		api     = NewPublicFilterAPI(backend, false)
+		api     = NewPublicFilterAPI(backend, false, deadline)
 
 		testCases = []struct {
 			crit    FilterCriteria
@@ -314,7 +319,7 @@ func TestInvalidLogFilterCreation(t *testing.T) {
 	var (
 		db      = rawdb.NewMemoryDatabase()
 		backend = &testBackend{db: db}
-		api     = NewPublicFilterAPI(backend, false)
+		api     = NewPublicFilterAPI(backend, false, deadline)
 	)
 
 	// different situations where log filter creation should fail.
@@ -336,7 +341,7 @@ func TestInvalidGetLogsRequest(t *testing.T) {
 	var (
 		db        = rawdb.NewMemoryDatabase()
 		backend   = &testBackend{db: db}
-		api       = NewPublicFilterAPI(backend, false)
+		api       = NewPublicFilterAPI(backend, false, deadline)
 		blockHash = common.HexToHash("0x1111111111111111111111111111111111111111111111111111111111111111")
 	)
 
@@ -361,7 +366,7 @@ func TestLogFilter(t *testing.T) {
 	var (
 		db      = rawdb.NewMemoryDatabase()
 		backend = &testBackend{db: db}
-		api     = NewPublicFilterAPI(backend, false)
+		api     = NewPublicFilterAPI(backend, false, deadline)
 
 		firstAddr      = common.HexToAddress("0x1111111111111111111111111111111111111111")
 		secondAddr     = common.HexToAddress("0x2222222222222222222222222222222222222222")
@@ -475,7 +480,7 @@ func TestPendingLogsSubscription(t *testing.T) {
 	var (
 		db      = rawdb.NewMemoryDatabase()
 		backend = &testBackend{db: db}
-		api     = NewPublicFilterAPI(backend, false)
+		api     = NewPublicFilterAPI(backend, false, deadline)
 
 		firstAddr      = common.HexToAddress("0x1111111111111111111111111111111111111111")
 		secondAddr     = common.HexToAddress("0x2222222222222222222222222222222222222222")
@@ -601,6 +606,73 @@ func TestPendingLogsSubscription(t *testing.T) {
 	}
 }
 
+// TestPendingTxFilterDeadlock tests if the event loop hangs when pending
+// txes arrive at the same time that one of multiple filters is timing out.
+// Please refer to #22131 for more details.
+func TestPendingTxFilterDeadlock(t *testing.T) {
+	t.Parallel()
+	timeout := 100 * time.Millisecond
+
+	var (
+		db      = rawdb.NewMemoryDatabase()
+		backend = &testBackend{db: db}
+		api     = NewPublicFilterAPI(backend, false, timeout)
+		done    = make(chan struct{})
+	)
+
+	go func() {
+		// Bombard feed with txes until signal was received to stop
+		i := uint64(0)
+		for {
+			select {
+			case <-done:
+				return
+			default:
+			}
+
+			tx := types.NewTransaction(i, common.HexToAddress("0xb794f5ea0ba39494ce83a213fffba74279579268"), new(big.Int), 0, new(big.Int), nil)
+			backend.txFeed.Send(core.NewTxsEvent{Txs: []*types.Transaction{tx}})
+			i++
+		}
+	}()
+
+	// Create a bunch of filters that will
+	// timeout either in 100ms or 200ms
+	fids := make([]rpc.ID, 20)
+	for i := 0; i < len(fids); i++ {
+		fid := api.NewPendingTransactionFilter()
+		fids[i] = fid
+		// Wait for at least one tx to arrive in filter
+		for {
+			hashes, err := api.GetFilterChanges(fid)
+			if err != nil {
+				t.Fatalf("Filter should exist: %v\n", err)
+			}
+			if len(hashes.([]common.Hash)) > 0 {
+				break
+			}
+			runtime.Gosched()
+		}
+	}
+
+	// Wait until filters have timed out
+	time.Sleep(3 * timeout)
+
+	// If tx loop doesn't consume `done` after a second
+	// it's hanging.
+	select {
+	case done <- struct{}{}:
+		// Check that all filters have been uninstalled
+		for _, fid := range fids {
+			if _, err := api.GetFilterChanges(fid); err == nil {
+				t.Errorf("Filter %s should have been uninstalled\n", fid)
+			}
+		}
+	case <-time.After(1 * time.Second):
+		t.Error("Tx sending loop hangs")
+	}
+}
+
 func flattenLogs(pl [][]*types.Log) []*types.Log {
 	var logs []*types.Log
 	for _, l := range pl {
```

### les/client.go
```diff
@@ -252,7 +252,7 @@ func (s *LightEthereum) APIs() []rpc.API {
 		}, {
 			Namespace: "eth",
 			Version:   "1.0",
-			Service:   filters.NewPublicFilterAPI(s.ApiBackend, true),
+			Service:   filters.NewPublicFilterAPI(s.ApiBackend, true, 5*time.Minute),
 			Public:    true,
 		}, {
 			Namespace: "net",
```
