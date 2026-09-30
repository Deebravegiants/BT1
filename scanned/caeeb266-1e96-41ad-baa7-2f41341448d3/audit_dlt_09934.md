# [?] Merge pull request #1851 from yoomee1313/fix-potential-deadlock-in-filter-timeout

## Summary
Severity: Unknown
Chain: Kaia
Component: kaiachain/kaia
Published: 2023-05-25
Source: https://github.com/kaiachain/kaia/commit/2869e65f140d860a8248337a3281c8b6104bde37
Type: security-commit

## Details
Merge pull request #1851 from yoomee1313/fix-potential-deadlock-in-filter-timeout

filters: ensure that filter unsubscription requests are not blocked

## Patch
### node/cn/filters/api.go
```diff
@@ -41,7 +41,7 @@ import (
 )
 
 var (
-	deadline = 5 * time.Minute // consider a filter inactive if it has not been polled for within deadline
+	defaultFilterDeadline = 5 * time.Minute // consider a filter inactive if it has not been polled for within deadline
 
 	getLogsCxtKeyMaxItems = "maxItems"       // the value of the context key should have the type of GetLogsMaxItems
 	GetLogsDeadline       = 10 * time.Second // execution deadlines for getLogs and getFilterLogs APIs
@@ -69,6 +69,9 @@ type PublicFilterAPI struct {
 	events    *EventSystem
 	filtersMu sync.Mutex
 	filters   map[rpc.ID]*filter
+
+	// this field is for test. it makes the filter timeout more flexible when testing
+	timeout time.Duration
 }
 
 // NewPublicFilterAPI returns a new PublicFilterAPI instance.
@@ -79,6 +82,7 @@ func NewPublicFilterAPI(backend Backend, lightMode bool) *PublicFilterAPI {
 		chainDB: backend.ChainDB(),
 		events:  NewEventSystem(backend.EventMux(), backend, lightMode),
 		filters: make(map[rpc.ID]*filter),
+		timeout: defaultFilterDeadline,
 	}
 	go api.timeoutLoop()
 
@@ -88,20 +92,30 @@ func NewPublicFilterAPI(backend Backend, lightMode bool) *PublicFilterAPI {
 // timeoutLoop runs every 5 minutes and deletes filters that have not been recently used.
 // Tt is started when the api is created.
 func (api *PublicFilterAPI) timeoutLoop() {
-	ticker := time.NewTicker(5 * time.Minute)
+	var toUninstall []*Subscription
+	ticker := time.NewTicker(api.timeout)
+	defer ticker.Stop()
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
 
@@ -117,7 +131,7 @@ func (api *PublicFilterAPI) NewPendingTransactionFilter() rpc.ID {
 	)
 
 	api.filtersMu.Lock()
-	api.filters[pendingTxSub.ID] = &filter{typ: PendingTransactionsSubscription, deadline: time.NewTimer(deadline), hashes: make([]common.Hash, 0), s: pendingTxSub}
+	api.filters[pendingTxSub.ID] = &filter{typ: PendingTransactionsSubscription, deadline: time.NewTimer(api.timeout), hashes: make([]common.Hash, 0), s: pendingTxSub}
 	api.filtersMu.Unlock()
 
 	go func() {
@@ -185,7 +199,7 @@ func (api *PublicFilterAPI) NewBlockFilter() rpc.ID {
 	)
 
 	api.filtersMu.Lock()
-	api.filters[headerSub.ID] = &filter{typ: BlocksSubscription, deadline: time.NewTimer(deadline), hashes: make([]common.Hash, 0), s: headerSub}
+	api.filters[headerSub.ID] = &filter{typ: BlocksSubscription, deadline: time.NewTimer(api.timeout), hashes: make([]common.Hash, 0), s: headerSub}
 	api.filtersMu.Unlock()
 
 	go func() {
@@ -331,7 +345,7 @@ func (api *PublicFilterAPI) NewFilter(crit FilterCriteria) (rpc.ID, error) {
 	}
 
 	api.filtersMu.Lock()
-	api.filters[logsSub.ID] = &filter{typ: LogsSubscription, crit: crit, deadline: time.NewTimer(deadline), logs: make([]*types.Log, 0), s: logsSub}
+	api.filters[logsSub.ID] = &filter{typ: LogsSubscription, crit: crit, deadline: time.NewTimer(api.timeout), logs: make([]*types.Log, 0), s: logsSub}
 	api.filtersMu.Unlock()
 
 	go func() {
@@ -450,7 +464,7 @@ func (api *PublicFilterAPI) GetFilterChanges(id rpc.ID) (interface{}, error) {
 			// receive timer value and reset timer
 			<-f.deadline.C
 		}
-		f.deadline.Reset(deadline)
+		f.deadline.Reset(api.timeout)
 
 		switch f.typ {
 		case PendingTransactionsSubscription, BlocksSubscription:
```

### node/cn/filters/filter_system_test.go
```diff
@@ -26,6 +26,7 @@ import (
 	"math/big"
 	"math/rand"
 	"reflect"
+	"runtime"
 	"testing"
 	"time"
 
@@ -630,3 +631,84 @@ func TestPendingLogsSubscription(t *testing.T) {
 		}
 	}
 }
+
+// TestPendingTxFilterDeadlock tests if the event loop hangs when pending
+// txs arrive at the same time that one of multiple filters is timing out.
+func TestPendingTxFilterDeadlock(t *testing.T) {
+	t.Parallel()
+	timeout := 100 * time.Millisecond
+
+	var (
+		mux        = new(event.TypeMux)
+		db         = database.NewMemoryDBManager()
+		txFeed     = new(event.Feed)
+		rmLogsFeed = new(event.Feed)
+		logsFeed   = new(event.Feed)
+		chainFeed  = new(event.Feed)
+		backend    = &testBackend{mux, db, 0, txFeed, rmLogsFeed, logsFeed, chainFeed, params.TestChainConfig}
+		done       = make(chan struct{})
+	)
+
+	// instead of using NewPublicFilterAPI, define it directly
+	// It is for faster test (timeout: 5minute -> 100millisecond)
+	api := &PublicFilterAPI{
+		backend: backend,
+		mux:     backend.EventMux(),
+		chainDB: backend.ChainDB(),
+		events:  NewEventSystem(backend.EventMux(), backend, false),
+		filters: make(map[rpc.ID]*filter),
+		timeout: timeout,
+	}
+	go api.timeoutLoop()
+
+	go func() {
+		// Bombard feed with txs until signal was received to stop
+		i := uint64(0)
+		for {
+			select {
+			case <-done:
+				return
+			default:
+			}
+
+			tx := types.NewTransaction(i, common.HexToAddress("0xb794f5ea0ba39494ce83a213fffba74279579268"), new(big.Int), 0, new(big.Int), nil)
+			backend.txFeed.Send(blockchain.NewTxsEvent{Txs: []*types.Transaction{tx}})
+			i++
+		}
+	}()
+
+	// Create a bunch of filters
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
```
