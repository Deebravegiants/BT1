# [?] p2p/discover: avoid deadlock between waitForNodes and node additions (#21064)

## Summary
Severity: Unknown
Chain: Ethereum
Component: erigontech/erigon
Published: 2026-05-19
Source: https://github.com/erigontech/erigon/commit/687b534a64ef57d174bc0ed09f4cd1a059e73bc5
Type: security-commit

## Details
p2p/discover: avoid deadlock between waitForNodes and node additions (#21064)

This change fixes a deadlock in peer discovery that can happen after the
routing table runs low on nodes and the iterator falls back to
`waitForNodes`. In that state, a node-add path can end up sending on the
table feed while holding the table mutex, while `waitForNodes` is trying
to wake up and reacquire the same mutex. If the timing lines up, both
sides can block each other and discovery stops making progress.

The fix decouples `waitForNodes` from direct feed consumption on the
mutex-taking goroutine. Instead, it subscribes once and forwards feed
activity through a buffered notification channel, so node-add paths are
no longer blocked by the waiter trying to reenter the table lock. A
regression test is included to cover this locking pattern and make sure
node additions continue to complete while `waitForNodes` is active.

https://github.com/ethereum/go-ethereum/issues/34881

---------

Co-authored-by: Alex Sharov <AskAlexSharov@gmail.com>

## Patch
### p2p/discover/table.go
```diff
@@ -744,35 +744,66 @@ func (tab *Table) deleteNode(n *enode.Node) {
 
 // waitForNodes blocks until the table contains at least n nodes.
 func (tab *Table) waitForNodes(ctx context.Context, n int) error {
+	// Wrap ctx so the forwarder goroutine exits when waitForNodes returns,
+	// regardless of whether the caller's ctx is canceled.
+	ctx, cancel := context.WithCancel(ctx)
+	defer cancel()
+
+	// Set up a notification channel that gets unblocked when there was any activity on
+	// the table. Ultimately this reads from the table's nodeFeed, but can't use the feed
+	// directly on the same goroutine that takes Table.mutex, it would deadlock.
+	var notify chan struct{}
+	var notifyErr error
+	initsub := func() event.Subscription {
+		notify = make(chan struct{}, 1)
+		newnode := make(chan *enode.Node, 1)
+		sub := tab.nodeFeed.Subscribe(newnode)
+		go func() {
+			defer close(notify)
+			for {
+				select {
+				case <-newnode:
+					select {
+					case notify <- struct{}{}:
+					default:
+					}
+				case <-ctx.Done():
+					notifyErr = ctx.Err()
+					return
+				case <-tab.closeReq:
+					notifyErr = errClosed
+					return
+				}
+			}
+		}()
+		return sub
+	}
+
 	getlength := func() (count int) {
 		for _, b := range &tab.buckets {
 			count += len(b.entries)
 		}
 		return count
 	}
 
-	var ch chan *enode.Node
 	for {
 		tab.mutex.Lock()
 		if getlength() >= n {
 			tab.mutex.Unlock()
 			return nil
 		}
-		if ch == nil {
-			// Init subscription.
-			ch = make(chan *enode.Node)
-			sub := tab.nodeFeed.Subscribe(ch)
+		if notify == nil {
+			// Lazily init the subscription. Do this while holding the
+			// lock so we don't miss any events that change the node count.
+			sub := initsub()
 			defer sub.Unsubscribe()
 		}
 		tab.mutex.Unlock()
 
-		// Wait for a node add event.
-		select {
-		case <-ch:
-		case <-ctx.Done():
-			return ctx.Err()
-		case <-tab.closeReq:
-			return errClosed
+		// Wait for table event.
+		if _, ok := <-notify; !ok {
+			break
 		}
 	}
+	return notifyErr
 }
```

### p2p/discover/table_test.go
```diff
@@ -20,6 +20,7 @@
 package discover
 
 import (
+	"context"
 	"crypto/ecdsa"
 	"fmt"
 	"math/rand"
@@ -563,3 +564,41 @@ func newkey() *ecdsa.PrivateKey {
 	}
 	return key
 }
+
+// This test checks that waitForNodes does not deadlock with addFoundNode.
+func TestTable_waitForNodesLocking(t *testing.T) {
+	transport := newPingRecorder()
+	tab, db := newTestTable(transport, Config{})
+	defer db.Close()
+	defer tab.close()
+	<-tab.initDone
+
+	// waitForNodes will never reach this count, so it stays subscribed
+	// to nodeFeed and looping for the duration of the test.
+	waitCtx, cancelWait := context.WithCancel(context.Background())
+	defer cancelWait()
+	waitDone := make(chan struct{})
+	go func() {
+		defer close(waitDone)
+		tab.waitForNodes(waitCtx, 1<<20)
+	}()
+
+	// Call addFoundNode in a loop to send to the feed repeatedly.
+	addDone := make(chan struct{})
+	go func() {
+		defer close(addDone)
+		for i := range 10000 {
+			d := 240 + (i % 17)
+			n := nodeAtDistance(tab.self().ID(), d, intIP(i))
+			tab.addFoundNode(n, true)
+		}
+	}()
+
+	select {
+	case <-addDone:
+		cancelWait()
+		<-waitDone
+	case <-time.After(10 * time.Second):
+		t.Fatal("deadlock detected: add loop did not finish within 10s")
+	}
+}
```
