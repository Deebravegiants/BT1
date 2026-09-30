# [?] Recover from panic in HandleTransaction to prevent peer crash (#5472)

## Summary
Severity: Unknown
Chain: Hyperledger Fabric
Component: hyperledger/fabric
Published: 2026-05-06
Source: https://github.com/hyperledger/fabric/commit/6a673975ced5a050d2e63e0a2c2d78283daf5ccb
Type: security-commit

## Details
Recover from panic in HandleTransaction to prevent peer crash (#5472)

When a transaction times out during a range query, the timeout path
closes LevelDB iterators while the handler goroutine is still using
them, causing a nil pointer dereference that crashes the peer.

Add a deferred recover() in HandleTransaction to catch such panics
and return an error response instead of crashing. This is safe because
the transaction has already timed out and the resources are being freed.

The panic value is logged but not included in the response payload to
avoid violating endorsement determinism across peers. Metrics are
recorded in the recover path to match the normal code path.

Also adds regression tests that verify the panic is recovered and
an error response is sent.

Fixes #5048

Signed-off-by: Jaskirat-s7 <jaskiratsingh7812@gmail.com>

## Patch
### core/chaincode/handler.go
```diff
@@ -245,12 +245,41 @@ type handleFunc func(*pb.ChaincodeMessage, *TransactionContext) (*pb.ChaincodeMe
 // returned by the delegate are sent to the chat stream. Any errors returned by the
 // delegate are packaged as chaincode error messages.
 func (h *Handler) HandleTransaction(msg *pb.ChaincodeMessage, delegate handleFunc) {
+	startTime := time.Now()
+	meterLabels := []string{
+		"type", msg.Type.String(),
+		"channel", msg.ChannelId,
+		"chaincode", h.chaincodeID,
+	}
+
+	// Recover from panics that can occur when the transaction context is cleaned up
+	// (e.g., iterators closed) due to execution timeout while this goroutine is still
+	// actively using those resources. This prevents peer crashes from nil pointer
+	// dereferences in the underlying LevelDB iterator.
+	// See https://github.com/hyperledger/fabric/issues/5048
+	defer func() {
+		if r := recover(); r != nil {
+			chaincodeLogger.Errorf("[%s] Recovered from panic handling %s: %v", shorttxid(msg.Txid), msg.Type, r)
+			resp := &pb.ChaincodeMessage{
+				Type:      pb.ChaincodeMessage_ERROR,
+				Payload:   []byte(fmt.Sprintf("%s failed: transaction ID: %s: panic during execution", msg.Type, msg.Txid)),
+				Txid:      msg.Txid,
+				ChannelId: msg.ChannelId,
+			}
+			h.ActiveTransactions.Remove(msg.ChannelId, msg.Txid)
+			h.serialSendAsync(resp)
+
+			meterLabels = append(meterLabels, "success", "false")
+			h.Metrics.ShimRequestDuration.With(meterLabels...).Observe(time.Since(startTime).Seconds())
+			h.Metrics.ShimRequestsCompleted.With(meterLabels...).Add(1)
+		}
+	}()
+
 	chaincodeLogger.Debugf("[%s] handling %s from chaincode", shorttxid(msg.Txid), msg.Type.String())
 	if !h.registerTxid(msg) {
 		return
 	}
 
-	startTime := time.Now()
 	var txContext *TransactionContext
 	var err error
 	if msg.Type == pb.ChaincodeMessage_INVOKE_CHAINCODE {
@@ -259,11 +288,6 @@ func (h *Handler) HandleTransaction(msg *pb.ChaincodeMessage, delegate handleFun
 		txContext, err = h.isValidTxSim(msg.ChannelId, msg.Txid, "no ledger context")
 	}
 
-	meterLabels := []string{
-		"type", msg.Type.String(),
-		"channel", msg.ChannelId,
-		"chaincode", h.chaincodeID,
-	}
 	h.Metrics.ShimRequestsReceived.With(meterLabels...).Add(1)
 
 	var resp *pb.ChaincodeMessage
```

### core/chaincode/handler_test.go
```diff
@@ -495,6 +495,43 @@ var _ = Describe("Handler", func() {
 				}))
 			})
 		})
+
+		// Regression test for https://github.com/hyperledger/fabric/issues/5048
+		// When a transaction times out during a range query, the timeout path closes
+		// the LevelDB iterator while the handler goroutine is still using it, causing
+		// a nil pointer dereference panic. The recover() in HandleTransaction prevents
+		// this from crashing the peer.
+		Context("when the delegate panics", func() {
+			It("recovers and sends an error response", func() {
+				panickingDelegate := func(msg *pb.ChaincodeMessage, txContext *chaincode.TransactionContext) (*pb.ChaincodeMessage, error) {
+					panic("simulated nil pointer dereference from closed iterator")
+				}
+
+				Expect(func() {
+					handler.HandleTransaction(incomingMessage, panickingDelegate)
+				}).NotTo(Panic())
+
+				Eventually(fakeChatStream.SendCallCount).Should(Equal(1))
+				msg := fakeChatStream.SendArgsForCall(0)
+				Expect(msg.Type).To(Equal(pb.ChaincodeMessage_ERROR))
+				Expect(msg.Txid).To(Equal("tx-id"))
+				Expect(msg.ChannelId).To(Equal("channel-id"))
+				Expect(string(msg.Payload)).To(ContainSubstring("panic during execution"))
+			})
+
+			It("deregisters the transaction ID", func() {
+				panickingDelegate := func(msg *pb.ChaincodeMessage, txContext *chaincode.TransactionContext) (*pb.ChaincodeMessage, error) {
+					panic("simulated panic")
+				}
+
+				handler.HandleTransaction(incomingMessage, panickingDelegate)
+
+				Expect(fakeTransactionRegistry.RemoveCallCount()).To(Equal(1))
+				channelID, transactionID := fakeTransactionRegistry.RemoveArgsForCall(0)
+				Expect(channelID).To(Equal("channel-id"))
+				Expect(transactionID).To(Equal("tx-id"))
+			})
+		})
 	})
 
 	Describe("HandlePutState", func() {
```
