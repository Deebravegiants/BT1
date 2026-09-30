# [?] eth/protocols/eth: fix deadlock when re-requesting partial receipts (#35537)

## Summary
Severity: Unknown
Chain: Ethereum
Component: ethereum/go-ethereum
Published: 2026-08-25
Source: https://github.com/ethereum/go-ethereum/commit/c57bbe4174252e4315532bffd13de93a87744d89
Type: security-commit

## Details
eth/protocols/eth: fix deadlock when re-requesting partial receipts (#35537)

When an eth/70 receipts response arrives with LastBlockIncomplete set,
requestPartialReceipts re-requested the remainder while holding
receiptBufferLock across the dispatch. That dispatch blocks until the
dispatcher loop accepts the request. If the loop is concurrently
cancelling a request for that peer, its cleanup takes the same
receiptBufferLock. The dispatcher then waits for the lock the re-request
holds while the re-request waits on a channel only the dispatcher reads.

The fix releases the lock before sending and routes the follow-up through
the dispatcher as a new resend request.

---------

Co-authored-by: Gary Rong <garyrong0905@gmail.com>

## Patch
### eth/protocols/eth/dispatcher.go
```diff
@@ -52,6 +52,7 @@ type Request struct {
 	want     uint64      // Message code of the response packet
 	numItems int         // Number of requested items
 	data     interface{} // Data content of the request packet
+	cleanup  func()      // Optional callback to release protocol-specific state if the request dies unfulfilled
 
 	Peer string    // Demultiplexer if cross-peer requests are batched together
 	Sent time.Time // Timestamp when the request was sent
@@ -94,6 +95,18 @@ type cancel struct {
 	fail chan error
 }
 
+// resend is a maintenance type on the dispatcher to send a follow-up packet
+// continuing a pending request under its original id. Routing it through the
+// dispatcher serializes the continuation against cancellation: the follow-up
+// is only sent if the original request is still pending.
+type resend struct {
+	id   uint64      // Request ID to continue
+	code uint64      // Message code of the follow-up packet
+	size int         // Number of items requested by the follow-up
+	data interface{} // Data content of the follow-up packet
+	fail chan error
+}
+
 // Response is a reply packet to a previously created request. It is delivered
 // on the channel assigned by the requester subsystem and contains the original
 // request embedded to allow uniquely matching it caller side.
@@ -138,6 +151,25 @@ func (p *Peer) dispatchRequest(req *Request) error {
 	}
 }
 
+// dispatchResend schedules a follow-up packet continuing a pending request,
+// blocking until it's sent. The follow-up is silently dropped if the original
+// request has already been cancelled or fulfilled.
+func (p *Peer) dispatchResend(id uint64, code uint64, size int, data interface{}) error {
+	resendOp := &resend{
+		id:   id,
+		code: code,
+		size: size,
+		data: data,
+		fail: make(chan error),
+	}
+	select {
+	case p.reqResend <- resendOp:
+		return <-resendOp.fail
+	case <-p.term:
+		return errDisconnected
+	}
+}
+
 // dispatchResponse fulfils a pending request and delivers it to the requested
 // sink.
 func (p *Peer) dispatchResponse(res *Response, metadata func() interface{}) error {
@@ -206,19 +238,46 @@ loop:
 				Size:     req.numItems,
 			}
 			if err := p.tracker.Track(treq); err != nil {
+				if req.cleanup != nil {
+					req.cleanup()
+				}
 				reqOp.fail <- err
 				continue loop
 			}
 			if err := p2p.Send(p.rw, req.code, req.data); err != nil {
+				if req.cleanup != nil {
+					req.cleanup()
+				}
 				reqOp.fail <- err
 				continue loop
 			}
+			pending[req.id] = req
+			reqOp.fail <- nil
 
-			// do not overwrite if it is re-request
-			if _, ok := pending[req.id]; !ok {
-				pending[req.id] = req
+		case resendOp := <-p.reqResend:
+			// Only continue a request that is still pending: if it has been
+			// cancelled or fulfilled in the meantime, drop the follow-up
+			// silently instead of re-requesting on behalf of nobody.
+			req := pending[resendOp.id]
+			if req == nil {
+				resendOp.fail <- nil
+				continue loop
 			}
-			reqOp.fail <- nil
+			treq := tracker.Request{
+				ID:       req.id,
+				ReqCode:  req.code,
+				RespCode: req.want,
+				Size:     resendOp.size,
+			}
+			if err := p.tracker.Track(treq); err != nil {
+				resendOp.fail <- err
+				continue loop
+			}
+			if err := p2p.Send(p.rw, resendOp.code, resendOp.data); err != nil {
+				resendOp.fail <- err
+				continue loop
+			}
+			resendOp.fail <- nil
 
 		case cancelOp := <-p.reqCancel:
 			// Retrieve the pending request to cancel and short circuit if it
@@ -228,15 +287,12 @@ loop:
 				cancelOp.fail <- nil
 				continue
 			}
-			// Stop tracking the request
+			// Stop tracking the request and release any protocol-specific
+			// state tied to it.
 			delete(pending, cancelOp.id)
-
-			// Not sure if the request is about the receipt, but remove it anyway.
-			// TODO(rjl493456442, bosul): investigate whether we can avoid leaking peer fields here.
-			p.receiptBufferLock.Lock()
-			delete(p.receiptBuffer, cancelOp.id)
-			p.receiptBufferLock.Unlock()
-
+			if req.cleanup != nil {
+				req.cleanup()
+			}
 			cancelOp.fail <- nil
 
 		case resOp := <-p.resDispatch:
```

### eth/protocols/eth/peer.go
```diff
@@ -76,6 +76,7 @@ type Peer struct {
 	tracker     *tracker.Tracker
 	reqDispatch chan *request  // Dispatch channel to send requests and track then until fulfillment
 	reqCancel   chan *cancel   // Dispatch channel to cancel pending requests and untrack them
+	reqResend   chan *resend   // Dispatch channel to send follow-ups for still-pending requests
 	resDispatch chan *response // Dispatch channel to fulfil pending requests and untrack them
 
 	chainConfig *params.ChainConfig // Chain configuration for fork-aware validation
@@ -102,6 +103,7 @@ func NewPeer(version uint, p *p2p.Peer, rw p2p.MsgReadWriter, txpool TxPool, blo
 		tracker:       tracker.New(cap, id, 5*time.Minute),
 		reqDispatch:   make(chan *request),
 		reqCancel:     make(chan *cancel),
+		reqResend:     make(chan *resend),
 		resDispatch:   make(chan *response),
 		txpool:        txpool,
 		blobpool:      blobpool,
@@ -466,6 +468,14 @@ func (p *Peer) RequestReceipts(hashes []common.Hash, gasUsed []uint64, timestamp
 				FirstBlockReceiptIndex: 0,
 				GetReceiptsRequest:     hashes,
 			},
+			// The buffer entry lives and dies with the request: the dispatcher
+			// releases it if the request is cancelled or fails to send, while
+			// a completed response consumes it on the delivery path.
+			cleanup: func() {
+				p.receiptBufferLock.Lock()
+				delete(p.receiptBuffer, id)
+				p.receiptBufferLock.Unlock()
+			},
 		}
 		p.receiptBufferLock.Lock()
 		p.receiptBuffer[id] = &receiptRequest{
@@ -493,33 +503,32 @@ func (p *Peer) RequestReceipts(hashes []common.Hash, gasUsed []uint64, timestamp
 	return req, nil
 }
 
-// HandlePartialReceipts re-request partial receipts
+// requestPartialReceipts re-requests the remainder of a partially delivered
+// receipt request under its original id.
 func (p *Peer) requestPartialReceipts(id uint64) error {
 	p.receiptBufferLock.Lock()
-	defer p.receiptBufferLock.Unlock()
 
 	// Do not re-request for the stale request
-	if _, ok := p.receiptBuffer[id]; !ok {
+	buffer, ok := p.receiptBuffer[id]
+	if !ok {
+		p.receiptBufferLock.Unlock()
 		return nil
 	}
-	lastBlock := len(p.receiptBuffer[id].list) - 1
-	lastReceipt := p.receiptBuffer[id].list[lastBlock].items.Len()
+	lastBlock := len(buffer.list) - 1
+	lastReceipt := buffer.list[lastBlock].items.Len()
 
-	hashes := p.receiptBuffer[id].request[lastBlock:]
+	hashes := buffer.request[lastBlock:]
+	p.receiptBufferLock.Unlock()
 
-	req := &Request{
-		id:   id,
-		sink: nil,
-		code: GetReceiptsMsg,
-		want: ReceiptsMsg,
-		data: &GetReceiptsPacket70{
-			RequestId:              id,
-			FirstBlockReceiptIndex: uint64(lastReceipt),
-			GetReceiptsRequest:     hashes,
-		},
-		numItems: len(hashes),
-	}
-	return p.dispatchRequest(req)
+	// The follow-up continues the original request under its original id,
+	// hand it to the dispatcher as a resend operation. The dispatcher only
+	// sends it if the original request is still pending, or silently drop
+	// the request if the original one is cancelled (with no error returned).
+	return p.dispatchResend(id, GetReceiptsMsg, len(hashes), &GetReceiptsPacket70{
+		RequestId:              id,
+		FirstBlockReceiptIndex: uint64(lastReceipt),
+		GetReceiptsRequest:     hashes,
+	})
 }
 
 // bufferReceipts validates a receipt packet and buffer the incomplete packet.
```
