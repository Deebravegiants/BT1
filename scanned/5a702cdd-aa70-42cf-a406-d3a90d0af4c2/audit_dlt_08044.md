# [?] swarm/network: fix data race in fetcher_test.go (#18469)

## Summary
Severity: Unknown
Chain: Celo
Component: celo-org/celo-blockchain
Published: 2019-01-17
Source: https://github.com/celo-org/celo-blockchain/commit/710775f43574ca7bdd039abb7474f34a4e4fe9fd
Type: security-commit

## Details
swarm/network: fix data race in fetcher_test.go (#18469)

(cherry picked from commit 19bfcbf9117f39f54f698a0953534d90c08e9930)

## Patch
### swarm/network/fetcher.go
```diff
@@ -26,27 +26,31 @@ import (
 	"github.com/ethereum/go-ethereum/swarm/storage"
 )
 
-var searchTimeout = 1 * time.Second
+const (
+	defaultSearchTimeout = 1 * time.Second
+	// maximum number of forwarded requests (hops), to make sure requests are not
+	// forwarded forever in peer loops
+	maxHopCount uint8 = 20
+)
 
 // Time to consider peer to be skipped.
 // Also used in stream delivery.
 var RequestTimeout = 10 * time.Second
 
-var maxHopCount uint8 = 20 // maximum number of forwarded requests (hops), to make sure requests are not forwarded forever in peer loops
-
 type RequestFunc func(context.Context, *Request) (*enode.ID, chan struct{}, error)
 
 // Fetcher is created when a chunk is not found locally. It starts a request handler loop once and
 // keeps it alive until all active requests are completed. This can happen:
 //     1. either because the chunk is delivered
-//     2. or becuse the requestor cancelled/timed out
+//     2. or because the requester cancelled/timed out
 // Fetcher self destroys itself after it is completed.
 // TODO: cancel all forward requests after termination
 type Fetcher struct {
 	protoRequestFunc RequestFunc     // request function fetcher calls to issue retrieve request for a chunk
 	addr             storage.Address // the address of the chunk to be fetched
 	offerC           chan *enode.ID  // channel of sources (peer node id strings)
 	requestC         chan uint8      // channel for incoming requests (with the hopCount value in it)
+	searchTimeout    time.Duration
 	skipCheck        bool
 }
 
@@ -79,7 +83,7 @@ func (r *Request) SkipPeer(nodeID string) bool {
 	}
 	t, ok := val.(time.Time)
 	if ok && time.Now().After(t.Add(RequestTimeout)) {
-		// deadine expired
+		// deadline expired
 		r.peersToSkip.Delete(nodeID)
 		return false
 	}
@@ -100,9 +104,10 @@ func NewFetcherFactory(request RequestFunc, skipCheck bool) *FetcherFactory {
 	}
 }
 
-// New contructs a new Fetcher, for the given chunk. All peers in peersToSkip are not requested to
-// deliver the given chunk. peersToSkip should always contain the peers which are actively requesting
-// this chunk, to make sure we don't request back the chunks from them.
+// New constructs a new Fetcher, for the given chunk. All peers in peersToSkip
+// are not requested to deliver the given chunk. peersToSkip should always
+// contain the peers which are actively requesting this chunk, to make sure we
+// don't request back the chunks from them.
 // The created Fetcher is started and returned.
 func (f *FetcherFactory) New(ctx context.Context, source storage.Address, peersToSkip *sync.Map) storage.NetFetcher {
 	fetcher := NewFetcher(source, f.request, f.skipCheck)
@@ -117,6 +122,7 @@ func NewFetcher(addr storage.Address, rf RequestFunc, skipCheck bool) *Fetcher {
 		protoRequestFunc: rf,
 		offerC:           make(chan *enode.ID),
 		requestC:         make(chan uint8),
+		searchTimeout:    defaultSearchTimeout,
 		skipCheck:        skipCheck,
 	}
 }
@@ -176,7 +182,7 @@ func (f *Fetcher) run(ctx context.Context, peers *sync.Map) {
 	// loop that keeps the fetching process alive
 	// after every request a timer is set. If this goes off we request again from another peer
 	// note that the previous request is still alive and has the chance to deliver, so
-	// rerequesting extends the search. ie.,
+	// requesting again extends the search. ie.,
 	// if a peer we requested from is gone we issue a new request, so the number of active
 	// requests never decreases
 	for {
@@ -209,13 +215,13 @@ func (f *Fetcher) run(ctx context.Context, peers *sync.Map) {
 		// search timeout: too much time passed since the last request,
 		// extend the search to a new peer if we can find one
 		case <-waitC:
-			log.Trace("search timed out: rerequesting", "request addr", f.addr)
+			log.Trace("search timed out: requesting", "request addr", f.addr)
 			doRequest = requested
 
 			// all Fetcher context closed, can quit
 		case <-ctx.Done():
 			log.Trace("terminate fetcher", "request addr", f.addr)
-			// TODO: send cancelations to all peers left over in peers map (i.e., those we requested from)
+			// TODO: send cancellations to all peers left over in peers map (i.e., those we requested from)
 			return
 		}
 
@@ -231,7 +237,7 @@ func (f *Fetcher) run(ctx context.Context, peers *sync.Map) {
 		// if wait channel is not set, set it to a timer
 		if requested {
 			if wait == nil {
-				wait = time.NewTimer(searchTimeout)
+				wait = time.NewTimer(f.searchTimeout)
 				defer wait.Stop()
 				waitC = wait.C
 			} else {
@@ -242,8 +248,8 @@ func (f *Fetcher) run(ctx context.Context, peers *sync.Map) {
 					default:
 					}
 				}
-				// reset the timer to go off after searchTimeout
-				wait.Reset(searchTimeout)
+				// reset the timer to go off after defaultSearchTimeout
+				wait.Reset(f.searchTimeout)
 			}
 		}
 		doRequest = false
```

### swarm/network/fetcher_test.go
```diff
@@ -284,15 +284,11 @@ func TestFetcherRetryOnTimeout(t *testing.T) {
 	requester := newMockRequester()
 	addr := make([]byte, 32)
 	fetcher := NewFetcher(addr, requester.doRequest, true)
+	// set searchTimeOut to low value so the test is quicker
+	fetcher.searchTimeout = 250 * time.Millisecond
 
 	peersToSkip := &sync.Map{}
 
-	// set searchTimeOut to low value so the test is quicker
-	defer func(t time.Duration) {
-		searchTimeout = t
-	}(searchTimeout)
-	searchTimeout = 250 * time.Millisecond
-
 	ctx, cancel := context.WithCancel(context.Background())
 	defer cancel()
 
@@ -359,11 +355,9 @@ func TestFetcherRequestQuitRetriesRequest(t *testing.T) {
 	addr := make([]byte, 32)
 	fetcher := NewFetcher(addr, requester.doRequest, true)
 
-	// make sure searchTimeout is long so it is sure the request is not retried because of timeout
-	defer func(t time.Duration) {
-		searchTimeout = t
-	}(searchTimeout)
-	searchTimeout = 10 * time.Second
+	// make sure the searchTimeout is long so it is sure the request is not
+	// retried because of timeout
+	fetcher.searchTimeout = 10 * time.Second
 
 	peersToSkip := &sync.Map{}
 
```
