# [?] tests: fix TestP2PRelay data race (#6316)

## Summary
Severity: Unknown
Chain: Algorand
Component: algorand/go-algorand
Published: 2025-05-07
Source: https://github.com/algorand/go-algorand/commit/005bf7eca3e0145a69d957178458850f53a5b126
Type: security-commit

## Details
tests: fix TestP2PRelay data race (#6316)

## Patch
### network/p2pNetwork_test.go
```diff
@@ -40,6 +40,7 @@ import (
 	"github.com/algorand/go-algorand/network/phonebook"
 	"github.com/algorand/go-algorand/protocol"
 	"github.com/algorand/go-algorand/test/partitiontest"
+	"github.com/algorand/go-deadlock"
 
 	pubsub "github.com/libp2p/go-libp2p-pubsub"
 	pb "github.com/libp2p/go-libp2p-pubsub/pb"
@@ -894,7 +895,11 @@ func TestP2PRelay(t *testing.T) {
 		return netA.hasPeers() && netB.hasPeers()
 	}, 2*time.Second, 50*time.Millisecond)
 
-	makeCounterHandler := func(numExpected int, counter *atomic.Uint32, msgs *[][]byte) ([]TaggedMessageValidatorHandler, chan struct{}) {
+	type logMessages struct {
+		msgs [][]byte
+		mu   deadlock.Mutex
+	}
+	makeCounterHandler := func(numExpected int, counter *atomic.Uint32, msgSink *logMessages) ([]TaggedMessageValidatorHandler, chan struct{}) {
 		counterDone := make(chan struct{})
 		counterHandler := []TaggedMessageValidatorHandler{
 			{
@@ -903,8 +908,10 @@ func TestP2PRelay(t *testing.T) {
 					ValidateHandleFunc
 				}{
 					ValidateHandleFunc(func(msg IncomingMessage) OutgoingMessage {
-						if msgs != nil {
-							*msgs = append(*msgs, msg.Data)
+						if msgSink != nil {
+							msgSink.mu.Lock()
+							msgSink.msgs = append(msgSink.msgs, msg.Data)
+							msgSink.mu.Unlock()
 						}
 						if count := counter.Add(1); int(count) >= numExpected {
 							close(counterDone)
@@ -970,8 +977,8 @@ func TestP2PRelay(t *testing.T) {
 
 	const expectedMsgs = 10
 	counter.Store(0)
-	var loggedMsgs [][]byte
-	counterHandler, counterDone = makeCounterHandler(expectedMsgs, &counter, &loggedMsgs)
+	var msgsSink logMessages
+	counterHandler, counterDone = makeCounterHandler(expectedMsgs, &counter, &msgsSink)
 	netA.ClearValidatorHandlers()
 	netA.RegisterValidatorHandlers(counterHandler)
 
@@ -991,10 +998,10 @@ func TestP2PRelay(t *testing.T) {
 	case <-counterDone:
 	case <-time.After(3 * time.Second):
 		if c := counter.Load(); c < expectedMsgs {
-			t.Logf("Logged messages: %v", loggedMsgs)
+			t.Logf("Logged messages: %v", msgsSink.msgs)
 			require.Failf(t, "One or more messages failed to reach destination network", "%d > %d", expectedMsgs, c)
 		} else if c > expectedMsgs {
-			t.Logf("Logged messages: %v", loggedMsgs)
+			t.Logf("Logged messages: %v", msgsSink.msgs)
 			require.Failf(t, "One or more messages that were expected to be dropped, reached destination network", "%d < %d", expectedMsgs, c)
 		}
 	}
```
