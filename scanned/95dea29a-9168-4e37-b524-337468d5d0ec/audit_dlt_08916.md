# [?] spy: fixed deadlock on subscriber disconnects

## Summary
Severity: Unknown
Chain: Wormhole
Component: wormhole-foundation/wormhole
Published: 2023-06-28
Source: https://github.com/wormhole-foundation/wormhole/commit/c882a6e062920b7b3722ab157cccc9f09e241c2e
Type: security-commit

## Details
spy: fixed deadlock on subscriber disconnects

Added the "sendTimeout" flag that specifies the timeout duration for sending
messages to subscribers.

## Patch
### node/cmd/spy/spy.go
```diff
@@ -8,6 +8,7 @@ import (
 	"net/http"
 	"os"
 	"sync"
+	"time"
 
 	"github.com/certusone/wormhole/node/pkg/common"
 	"github.com/certusone/wormhole/node/pkg/p2p"
@@ -44,6 +45,8 @@ var (
 	logLevel *string
 
 	spyRPC *string
+
+	sendTimeout *time.Duration
 )
 
 func init() {
@@ -58,6 +61,8 @@ func init() {
 	logLevel = SpyCmd.Flags().String("logLevel", "info", "Logging level (debug, info, warn, error, dpanic, panic, fatal)")
 
 	spyRPC = SpyCmd.Flags().String("spyRPC", "", "Listen address for gRPC interface")
+
+	sendTimeout = SpyCmd.Flags().Duration("sendTimeout", 5*time.Second, "Timeout for sending a message to a subscriber")
 }
 
 // SpyCmd represents the node command
@@ -133,7 +138,7 @@ func TransactionIdMatches(g *gossipv1.SignedBatchVAAWithQuorum, t *spyv1.BatchFi
 	return bytes.Equal(g.TxId, t.TxId)
 }
 
-// BatchMatchFilter asserts that the obervation matches the values of the filter.
+// BatchMatchFilter asserts that the observation matches the values of the filter.
 func BatchMatchesFilter(g *gossipv1.SignedBatchVAAWithQuorum, f *spyv1.BatchFilter) bool {
 	// check the chain ID
 	if g.ChainId != uint32(f.ChainId) {
@@ -171,7 +176,7 @@ func (s *spyServer) HandleGossipVAA(g *gossipv1.SignedVAAWithQuorum) error {
 		return err
 	}
 
-	// resType defines which oneof proto will be retuned - res type "SignedVaa" is *gossipv1.SignedVAAWithQuorum
+	// resType defines which oneof proto will be returned  - res type "SignedVaa" is *gossipv1.SignedVAAWithQuorum
 	resType := &spyv1.SubscribeSignedVAAByTypeResponse_SignedVaa{
 		SignedVaa: g,
 	}
@@ -224,7 +229,7 @@ func (s *spyServer) HandleGossipBatchVAA(g *gossipv1.SignedBatchVAAWithQuorum) e
 		return err
 	}
 
-	// resType defines which oneof proto will be retuned -
+	// resType defines which oneof proto will be returned -
 	// res type "SignedBatchVaa" is *gossipv1.SignedBatchVAAWithQuorum
 	resType := &spyv1.SubscribeSignedVAAByTypeResponse_SignedBatchVaa{
 		SignedBatchVaa: g,
@@ -260,7 +265,7 @@ func (s *spyServer) HandleGossipBatchVAA(g *gossipv1.SignedBatchVAAWithQuorum) e
 
 				// In order to make it easier for integrators, allow subscribing to BatchVAAs by
 				// EmitterFilter. Send BatchVAAs to subscriptions with an EmitterFilter that
-				// matches 1 (or more) Obervation(s) in the batch.
+				// matches 1 (or more) Observation(s) in the batch.
 
 				filterAddr := t.EmitterFilter.EmitterAddress
 
@@ -326,19 +331,27 @@ func (s *spyServer) SubscribeSignedVAA(req *spyv1.SubscribeSignedVAARequest, res
 	s.subsSignedVaaMu.Unlock()
 
 	defer func() {
-		s.subsSignedVaaMu.Lock()
-		defer s.subsSignedVaaMu.Unlock()
-		delete(s.subsSignedVaa, id)
+		for {
+			// The channel sender locks the subscription mutex before sending to the channel.
+			// If the channel is full, then the sender will block and we'll never be able to lock the mutex (resulting in deadlock).
+			// So we empty the channel before trying acquire the lock.
+			_ = DoWithTimeout(func() error { <-sub.ch; return nil }, time.Millisecond)
+			if s.subsSignedVaaMu.TryLock() {
+				delete(s.subsSignedVaa, id)
+				s.subsSignedVaaMu.Unlock()
+				return
+			}
+		}
 	}()
 
 	for {
 		select {
 		case <-resp.Context().Done():
 			return resp.Context().Err()
 		case msg := <-sub.ch:
-			if err := resp.Send(&spyv1.SubscribeSignedVAAResponse{
-				VaaBytes: msg.vaaBytes,
-			}); err != nil {
+			if err := DoWithTimeout(func() error {
+				return resp.Send(&spyv1.SubscribeSignedVAAResponse{VaaBytes: msg.vaaBytes})
+			}, *sendTimeout); err != nil {
 				return err
 			}
 		}
@@ -380,17 +393,27 @@ func (s *spyServer) SubscribeSignedVAAByType(req *spyv1.SubscribeSignedVAAByType
 	s.subsAllVaaMu.Unlock()
 
 	defer func() {
-		s.subsAllVaaMu.Lock()
-		defer s.subsAllVaaMu.Unlock()
-		delete(s.subsAllVaa, id)
+		for {
+			// The channel sender locks the subscription mutex before sending to the channel.
+			// If the channel is full, then the sender will block and we'll never be able to lock the mutex (resulting in deadlock).
+			// So we empty the channel before trying acquire the lock.
+			_ = DoWithTimeout(func() error { <-sub.ch; return nil }, time.Millisecond)
+			if s.subsAllVaaMu.TryLock() {
+				delete(s.subsAllVaa, id)
+				s.subsAllVaaMu.Unlock()
+				return
+			}
+		}
 	}()
 
 	for {
 		select {
 		case <-resp.Context().Done():
 			return resp.Context().Err()
 		case msg := <-sub.ch:
-			if err := resp.Send(msg); err != nil {
+			if err := DoWithTimeout(func() error {
+				return resp.Send(msg)
+			}, *sendTimeout); err != nil {
 				return err
 			}
 		}
@@ -405,6 +428,26 @@ func newSpyServer(logger *zap.Logger) *spyServer {
 	}
 }
 
+// DoWithTimeout runs f and returns its error. If the deadline d elapses first,
+// it returns a grpc DeadlineExceeded error instead.
+func DoWithTimeout(f func() error, d time.Duration) error {
+	errChan := make(chan error, 1)
+	go func() {
+		errChan <- f()
+		close(errChan)
+	}()
+	t := time.NewTimer(d)
+	select {
+	case <-t.C:
+		return status.Errorf(codes.DeadlineExceeded, "too slow")
+	case err := <-errChan:
+		if !t.Stop() {
+			<-t.C
+		}
+		return err
+	}
+}
+
 func spyServerRunnable(s *spyServer, logger *zap.Logger, listenAddr string) (supervisor.Runnable, *grpc.Server, error) {
 	l, err := net.Listen("tcp", listenAddr)
 	if err != nil {
@@ -461,13 +504,13 @@ func runSpy(cmd *cobra.Command, args []string) {
 	sendC := make(chan []byte)
 
 	// Inbound observations
-	obsvC := make(chan *gossipv1.SignedObservation, 50)
+	obsvC := make(chan *gossipv1.SignedObservation, 1024)
 
 	// Inbound observation requests
-	obsvReqC := make(chan *gossipv1.ObservationRequest, 50)
+	obsvReqC := make(chan *gossipv1.ObservationRequest, 1024)
 
 	// Inbound signed VAAs
-	signedInC := make(chan *gossipv1.SignedVAAWithQuorum, 50)
+	signedInC := make(chan *gossipv1.SignedVAAWithQuorum, 1024)
 
 	// Guardian set state managed by processor
 	gst := common.NewGuardianSetState(nil)
```
