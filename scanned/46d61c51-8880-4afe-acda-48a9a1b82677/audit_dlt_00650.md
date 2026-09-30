# [?] Fix panic on lightest mode client when requesting a block with unknown hash. (#1631)

## Summary
Severity: Unknown
Chain: Celo
Component: celo-org/celo-blockchain
Published: 2021-08-30
Source: https://github.com/celo-org/celo-blockchain/commit/43ae19064484233315e4dace800d16c19915e377
Type: security-commit

## Details
Fix panic on lightest mode client when requesting a block with unknown hash. (#1631)

Previously, if you use `eth_getBlock` on a lightest mode client, and specify a hash that doesn't correspond to a block, the entire client would crash due to a panic in client_handler.go.  This PR fixes that panic, and makes getting a block by an unknown hash return "unknown block", which is the desired behavior and also what you get when you request a block by an unknown number (a number that is higher than the last block's number).

This requires modifying the `HeaderRequest` ODR request type to properly work when receiving a response with no headers.  This PR modifies it to accept such responses if the request was by hash, but not if it was by number.  This opens the door for a malicious LES server to fool a light client into thinking there is no block with this hash, when in fact there is.  However, it's simpler and seems preferable to the alternative of querying all one's peers in case some of them are malicious this way, and only returning "unknown block" after querying all of them.  It's also preferable to the current status quo of malicious nodes being able to crash a lightest mode client by returning an empty response.  Note, too, that requesting the header by hash is only done through the RPC API and is not a common use-pattern by light client users.

## Patch
### les/client_handler.go
```diff
@@ -320,9 +320,11 @@ func (h *clientHandler) handleMsg(p *serverPeer) error {
 			headerRequested := h.backend.retriever.sentReqs[resp.ReqID]
 			h.backend.retriever.lock.RUnlock()
 			if headerRequested != nil {
-				contiguousHeaders := h.syncMode != downloader.LightestSync
-				if _, err := h.fetcher.chain.InsertHeaderChain(headers, 1, contiguousHeaders); err != nil {
-					return err
+				if len(headers) != 0 {
+					contiguousHeaders := h.syncMode != downloader.LightestSync
+					if _, err := h.fetcher.chain.InsertHeaderChain(headers, 1, contiguousHeaders); err != nil {
+						return err
+					}
 				}
 				deliverMsg = &Msg{
 					MsgType: MsgBlockHeaders,
```

### les/odr_requests.go
```diff
@@ -146,7 +146,7 @@ func (r *HeaderRequest) CanSend(peer *serverPeer) bool {
 
 // Request sends an ODR request to the LES network (implementation of LesOdrRequest)
 func (r *HeaderRequest) Request(reqId uint64, peer *serverPeer) error {
-	if r.Origin.Hash != (common.Hash{}) {
+	if r.isByHash() {
 		peer.Log().Debug("Requesting block header", "hash", r.Origin.Hash)
 		return peer.requestHeadersByHash(reqId, r.Origin.Hash, 1, 0, false)
 	} else {
@@ -155,6 +155,11 @@ func (r *HeaderRequest) Request(reqId uint64, peer *serverPeer) error {
 	}
 }
 
+// Whether the request specified the block hash (rather than block number)
+func (r *HeaderRequest) isByHash() bool {
+	return r.Origin.Hash != common.Hash{}
+}
+
 // Validate processes an ODR request reply message from the LES network
 // returns true and stores results in memory if the message was a valid reply
 // to the request (implementation of LesOdrRequest)
@@ -164,7 +169,15 @@ func (r *HeaderRequest) Validate(db ethdb.Database, msg *Msg) error {
 		return errInvalidMessageType
 	}
 	headers := msg.Obj.([]*types.Header)
-	if len(headers) != 1 {
+	if len(headers) == 0 && r.isByHash() {
+		// For requests by number, we only send to peers for which we know the block number
+		// is within the range of what they have, so if they don't send us the header we reject
+		// the response and try other peers.
+		// However, for requests by hash, we have no way of knowing ahead of time whether the peer
+		// should have it or not (e.g. what if there is no such block?).  So we need to accept
+		// 'no match' as a valid response, to avoid ODR endlessly trying to send to different peers.
+		return nil
+	} else if len(headers) != 1 {
 		return errInvalidEntryCount
 	}
 	if r.Origin.Hash != (common.Hash{}) && headers[0].Hash() != r.Origin.Hash {
```

### light/lightchain.go
```diff
@@ -298,7 +298,9 @@ func (lc *LightChain) GetBlockByHash(ctx context.Context, hash common.Hash) (*ty
 	number := lc.hc.GetBlockNumber(hash)
 	if number == nil {
 		header, err := GetHeaderByHash(ctx, lc.odr, hash)
-		if err != nil {
+		// Header may be nil, indicating the hash doesn't match any known blocks,
+		// which is a valid response to the ODR request.
+		if err != nil || header == nil {
 			return nil, errors.New("unknown block")
 		}
 		return lc.GetBlock(ctx, hash, header.Number.Uint64())
```

### light/odr.go
```diff
@@ -131,6 +131,11 @@ type HeaderRequest struct {
 // StoreResult handles storing the canonical hash if `InsertHeaderChain` has not already
 // This occurs if the total difficulty of the requested header is less than the current known TD.
 func (req *HeaderRequest) StoreResult(db ethdb.Database) {
+	if req.Header == nil {
+		// A nil header is a valid response when request the header by hash, as it indicates
+		// no known block with this hash.  In this case, there is nothing for us to do here.
+		return
+	}
 	if rawdb.ReadCanonicalHash(db, req.Header.Number.Uint64()) == (common.Hash{}) {
 		rawdb.WriteCanonicalHash(db, req.Header.Hash(), req.Header.Number.Uint64())
 	}
```
