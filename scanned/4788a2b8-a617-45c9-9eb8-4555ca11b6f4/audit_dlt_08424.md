# [?] rpc: fix panic when `Subscribe` is called (#4570)

## Summary
Severity: Unknown
Chain: Cosmos
Component: cometbft/cometbft
Published: 2020-03-16
Source: https://github.com/cometbft/cometbft/commit/c917c2ddfb825f8e5eeb1dce36cd486afd19d433
Type: security-commit

## Details
rpc: fix panic when `Subscribe` is called (#4570)

but HTTP client is not running.

`Subscribe`, `Unsubscribe(All)` methods return an error now.

Closes #4568

## Patch
### CHANGELOG_PENDING.md
```diff
@@ -22,3 +22,6 @@ Friendly reminder, we have a [bug bounty program](https://hackerone.com/tendermi
 - [privval] \#4534 Add `error` as a return value on`GetPubKey()`
 
 ### BUG FIXES:
+
+- [rpc] \#4568 Fix panic when `Subscribe` is called, but HTTP client is not running (@melekes)
+  `Subscribe`, `Unsubscribe(All)` methods return an error now.
```

### rpc/client/event_test.go
```diff
@@ -1,11 +1,13 @@
 package client_test
 
 import (
+	"context"
 	"fmt"
 	"reflect"
 	"testing"
 	"time"
 
+	"github.com/stretchr/testify/assert"
 	"github.com/stretchr/testify/require"
 
 	abci "github.com/tendermint/tendermint/abci/types"
@@ -135,3 +137,21 @@ func testTxEventsSent(t *testing.T, broadcastMethod string) {
 func TestClientsResubscribe(t *testing.T) {
 	// TODO(melekes)
 }
+
+func TestHTTPReturnsErrorIfClientIsNotRunning(t *testing.T) {
+	c := getHTTPClient()
+
+	// on Subscribe
+	_, err := c.Subscribe(context.Background(), "TestHeaderEvents",
+		types.QueryForEvent(types.EventNewBlockHeader).String())
+	assert.Error(t, err)
+
+	// on Unsubscribe
+	err = c.Unsubscribe(context.Background(), "TestHeaderEvents",
+		types.QueryForEvent(types.EventNewBlockHeader).String())
+	assert.Error(t, err)
+
+	// on UnsubscribeAll
+	err = c.UnsubscribeAll(context.Background(), "TestHeaderEvents")
+	assert.Error(t, err)
+}
```

### rpc/client/examples_test.go
```diff
@@ -3,6 +3,7 @@ package client_test
 import (
 	"bytes"
 	"fmt"
+	"log"
 
 	"github.com/tendermint/tendermint/abci/example/kvstore"
 	"github.com/tendermint/tendermint/rpc/client"
@@ -20,7 +21,7 @@ func ExampleHTTP_simple() {
 	rpcAddr := rpctest.GetConfig().RPC.ListenAddress
 	c, err := client.NewHTTP(rpcAddr, "/websocket")
 	if err != nil {
-		panic(err)
+		log.Fatal(err)
 	}
 
 	// Create a transaction
@@ -29,28 +30,28 @@ func ExampleHTTP_simple() {
 	tx := append(k, append([]byte("="), v...)...)
 
 	// Broadcast the transaction and wait for it to commit (rather use
-	// c.BroadcastTxSync though in production)
+	// c.BroadcastTxSync though in production).
 	bres, err := c.BroadcastTxCommit(tx)
 	if err != nil {
-		panic(err)
+		log.Fatal(err)
 	}
 	if bres.CheckTx.IsErr() || bres.DeliverTx.IsErr() {
-		panic("BroadcastTxCommit transaction failed")
+		log.Fatal("BroadcastTxCommit transaction failed")
 	}
 
 	// Now try to fetch the value for the key
 	qres, err := c.ABCIQuery("/key", k)
 	if err != nil {
-		panic(err)
+		log.Fatal(err)
 	}
 	if qres.Response.IsErr() {
-		panic("ABCIQuery failed")
+		log.Fatal("ABCIQuery failed")
 	}
 	if !bytes.Equal(qres.Response.Key, k) {
-		panic("returned key does not match queried key")
+		log.Fatal("returned key does not match queried key")
 	}
 	if !bytes.Equal(qres.Response.Value, v) {
-		panic("returned value does not match sent value")
+		log.Fatal("returned value does not match sent value")
 	}
 
 	fmt.Println("Sent tx     :", string(tx))
@@ -73,7 +74,7 @@ func ExampleHTTP_batching() {
 	rpcAddr := rpctest.GetConfig().RPC.ListenAddress
 	c, err := client.NewHTTP(rpcAddr, "/websocket")
 	if err != nil {
-		panic(err)
+		log.Fatal(err)
 	}
 
 	// Create our two transactions
@@ -92,36 +93,38 @@ func ExampleHTTP_batching() {
 
 	// Queue up our transactions
 	for _, tx := range txs {
+		// Broadcast the transaction and wait for it to commit (rather use
+		// c.BroadcastTxSync though in production).
 		if _, err := batch.BroadcastTxCommit(tx); err != nil {
-			panic(err)
+			log.Fatal(err)
 		}
 	}
 
 	// Send the batch of 2 transactions
 	if _, err := batch.Send(); err != nil {
-		panic(err)
+		log.Fatal(err)
 	}
 
 	// Now let's query for the original results as a batch
 	keys := [][]byte{k1, k2}
 	for _, key := range keys {
 		if _, err := batch.ABCIQuery("/key", key); err != nil {
-			panic(err)
+			log.Fatal(err)
 		}
 	}
 
 	// Send the 2 queries and keep the results
 	results, err := batch.Send()
 	if err != nil {
-		panic(err)
+		log.Fatal(err)
 	}
 
 	// Each result in the returned list is the deserialized result of each
 	// respective ABCIQuery response
 	for _, result := range results {
 		qr, ok := result.(*ctypes.ResultABCIQuery)
 		if !ok {
-			panic("invalid result type from ABCIQuery request")
+			log.Fatal("invalid result type from ABCIQuery request")
 		}
 		fmt.Println(string(qr.Response.Key), "=", string(qr.Response.Value))
 	}
```

### rpc/client/httpclient.go
```diff
@@ -37,6 +37,27 @@ indefinitely until successful.
 Request batching is available for JSON RPC requests over HTTP, which conforms to
 the JSON RPC specification (https://www.jsonrpc.org/specification#batch). See
 the example for more details.
+
+Example:
+
+		c, err := NewHTTP("http://192.168.1.10:26657", "/websocket")
+		if err != nil {
+			// handle error
+		}
+
+		// call Start/Stop if you're subscribing to events
+		err = c.Start()
+		if err != nil {
+			// handle error
+		}
+		defer c.Stop()
+
+		res, err := c.Status()
+		if err != nil {
+			// handle error
+		}
+
+		// handle result
 */
 type HTTP struct {
 	remote string
@@ -121,11 +142,16 @@ func NewHTTPWithClient(remote, wsEndpoint string, client *http.Client) (*HTTP, e
 	ctypes.RegisterAmino(cdc)
 	rc.SetCodec(cdc)
 
+	wsEvents, err := newWSEvents(cdc, remote, wsEndpoint)
+	if err != nil {
+		return nil, err
+	}
+
 	httpClient := &HTTP{
 		rpc:           rc,
 		remote:        remote,
 		baseRPCClient: &baseRPCClient{caller: rc},
-		WSEvents:      newWSEvents(cdc, remote, wsEndpoint),
+		WSEvents:      wsEvents,
 	}
 
 	return httpClient, nil
@@ -406,48 +432,51 @@ func (c *baseRPCClient) BroadcastEvidence(ev types.Evidence) (*ctypes.ResultBroa
 //-----------------------------------------------------------------------------
 // WSEvents
 
+var errNotRunning = errors.New("client is not running. Use .Start() method to start")
+
+// WSEvents is a wrapper around WSClient, which implements EventsClient.
 type WSEvents struct {
 	service.BaseService
 	cdc      *amino.Codec
 	remote   string
 	endpoint string
 	ws       *rpcclient.WSClient
 
-	mtx sync.RWMutex
-	// query -> chan
-	subscriptions map[string]chan ctypes.ResultEvent
+	mtx           sync.RWMutex
+	subscriptions map[string]chan ctypes.ResultEvent // query -> chan
 }
 
-func newWSEvents(cdc *amino.Codec, remote, endpoint string) *WSEvents {
-	wsEvents := &WSEvents{
+func newWSEvents(cdc *amino.Codec, remote, endpoint string) (*WSEvents, error) {
+	w := &WSEvents{
 		cdc:           cdc,
 		endpoint:      endpoint,
 		remote:        remote,
 		subscriptions: make(map[string]chan ctypes.ResultEvent),
 	}
+	w.BaseService = *service.NewBaseService(nil, "WSEvents", w)
 
-	wsEvents.BaseService = *service.NewBaseService(nil, "WSEvents", wsEvents)
-	return wsEvents
-}
-
-// OnStart implements service.Service by starting WSClient and event loop.
-func (w *WSEvents) OnStart() (err error) {
+	var err error
 	w.ws, err = rpcclient.NewWSClient(w.remote, w.endpoint, rpcclient.OnReconnect(func() {
 		// resubscribe immediately
 		w.redoSubscriptionsAfter(0 * time.Second)
 	}))
 	if err != nil {
-		return err
+		return nil, err
 	}
 	w.ws.SetCodec(w.cdc)
 	w.ws.SetLogger(w.Logger)
 
-	err = w.ws.Start()
-	if err != nil {
+	return w, nil
+}
+
+// OnStart implements service.Service by starting WSClient and event loop.
+func (w *WSEvents) OnStart() error {
+	if err := w.ws.Start(); err != nil {
 		return err
 	}
 
 	go w.eventListener()
+
 	return nil
 }
 
@@ -459,10 +488,17 @@ func (w *WSEvents) OnStop() {
 // Subscribe implements EventsClient by using WSClient to subscribe given
 // subscriber to query. By default, returns a channel with cap=1. Error is
 // returned if it fails to subscribe.
-// Channel is never closed to prevent clients from seeing an erroneus event.
+//
+// Channel is never closed to prevent clients from seeing an erroneous event.
+//
+// It returns an error if WSEvents is not running.
 func (w *WSEvents) Subscribe(ctx context.Context, subscriber, query string,
 	outCapacity ...int) (out <-chan ctypes.ResultEvent, err error) {
 
+	if !w.IsRunning() {
+		return nil, errNotRunning
+	}
+
 	if err := w.ws.Subscribe(ctx, query); err != nil {
 		return nil, err
 	}
@@ -484,7 +520,13 @@ func (w *WSEvents) Subscribe(ctx context.Context, subscriber, query string,
 
 // Unsubscribe implements EventsClient by using WSClient to unsubscribe given
 // subscriber from query.
+//
+// It returns an error if WSEvents is not running.
 func (w *WSEvents) Unsubscribe(ctx context.Context, subscriber, query string) error {
+	if !w.IsRunning() {
+		return errNotRunning
+	}
+
 	if err := w.ws.Unsubscribe(ctx, query); err != nil {
 		return err
 	}
@@ -501,7 +543,13 @@ func (w *WSEvents) Unsubscribe(ctx context.Context, subscriber, query string) er
 
 // UnsubscribeAll implements EventsClient by using WSClient to unsubscribe
 // given subscriber from all the queries.
+//
+// It returns an error if WSEvents is not running.
 func (w *WSEvents) UnsubscribeAll(ctx context.Context, subscriber string) error {
+	if !w.IsRunning() {
+		return errNotRunning
+	}
+
 	if err := w.ws.UnsubscribeAll(ctx); err != nil {
 		return err
 	}
```
