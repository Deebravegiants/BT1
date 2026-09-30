# [?] fix(rpc/v8): race condition in head subscription and duplicate pending tx (#2613)

## Summary
Severity: Unknown
Chain: Starknet
Component: NethermindEth/juno
Published: 2025-03-06
Source: https://github.com/NethermindEth/juno/commit/ba9b10e2528ff7974342b5ffd04b7ee814b35fe6
Type: security-commit

## Details
fix(rpc/v8): race condition in head subscription and duplicate pending tx (#2613)

fix: Fix race condition in head subscription and duplicate pending tx

## Patch
### rpc/v8/subscriptions.go
```diff
@@ -93,35 +93,36 @@ func (b *SubscriptionBlockID) UnmarshalJSON(data []byte) error {
 	return nil
 }
 
-// Currently the order of transactions is deterministic, so the transaction always execute on a deterministic state
-// Therefore, the emitted events are deterministic and we can use the transaction hash and event index to identify.
-type SentEvent struct {
-	TransactionHash felt.Felt
-	EventIndex      int
-}
+type on[T any] func(ctx context.Context, id uint64, event T) error
 
-// SubscribeEvents creates a WebSocket stream which will fire events for new Starknet events with applied filters
-func (h *Handler) SubscribeEvents(ctx context.Context, fromAddr *felt.Felt, keys [][]felt.Felt,
-	blockID *SubscriptionBlockID,
-) (SubscriptionID, *jsonrpc.Error) {
-	w, ok := jsonrpc.ConnFromContext(ctx)
-	if !ok {
-		return 0, jsonrpc.Err(jsonrpc.MethodNotFound, nil)
-	}
+type subscriber struct {
+	onStart   on[any]
+	onReorg   on[*sync.ReorgBlockRange]
+	onNewHead on[*core.Block]
+	onPending on[*core.Block]
+	onL1Head  on[*core.L1Head]
+}
 
-	lenKeys := len(keys)
-	for _, k := range keys {
-		lenKeys += len(k)
-	}
-	if lenKeys > rpccore.MaxEventFilterKeys {
-		return 0, rpccore.ErrTooManyKeysInFilter
+func getSubscription[T any](callback on[T], feed *feed.Feed[T]) (*feed.Subscription[T], <-chan T) {
+	if callback != nil {
+		sub := feed.SubscribeKeepLast()
+		recv := sub.Recv()
+		return sub, recv
 	}
+	return nil, nil
+}
 
-	requestedHeader, headHeader, rpcErr := h.resolveBlockRange(blockID)
-	if rpcErr != nil {
-		return 0, rpcErr
+func unsubscribeFeedSubscription[T any](sub *feed.Subscription[T]) {
+	if sub != nil {
+		sub.Unsubscribe()
 	}
+}
 
+func (h *Handler) subscribe(
+	ctx context.Context,
+	w jsonrpc.Conn,
+	subscriber subscriber,
+) (SubscriptionID, *jsonrpc.Error) {
 	id := h.idgen()
 	subscriptionCtx, subscriptionCtxCancel := context.WithCancel(ctx)
 	sub := &subscription{
@@ -130,45 +131,115 @@ func (h *Handler) SubscribeEvents(ctx context.Context, fromAddr *felt.Felt, keys
 	}
 	h.subscriptions.Store(id, sub)
 
-	newHeadsSub := h.newHeads.SubscribeKeepLast()
-	reorgSub := h.reorgs.SubscribeKeepLast() // as per the spec, reorgs are also sent in the events subscription
-	pendingSub := h.pendingBlock.SubscribeKeepLast()
+	reorgSub, reorgRecv := getSubscription(subscriber.onReorg, h.reorgs)
+	newHeadsSub, newHeadsRecv := getSubscription(subscriber.onNewHead, h.newHeads)
+	pendingSub, pendingRecv := getSubscription(subscriber.onPending, h.pendingBlock)
+	l1HeadSub, l1HeadRecv := getSubscription(subscriber.onL1Head, h.l1Heads)
+
 	sub.wg.Go(func() {
 		defer func() {
 			h.unsubscribe(sub, id)
-			newHeadsSub.Unsubscribe()
-			reorgSub.Unsubscribe()
-			pendingSub.Unsubscribe()
+			unsubscribeFeedSubscription(reorgSub)
+			unsubscribeFeedSubscription(l1HeadSub)
+			unsubscribeFeedSubscription(newHeadsSub)
+			unsubscribeFeedSubscription(pendingSub)
 		}()
 
-		// We still need to run this separately outside of the loop to capture the latest block before subscription.
-		h.processEvents(subscriptionCtx, w, id, requestedHeader.Number, headHeader.Number, fromAddr, keys, nil)
-
-		nextBlock := headHeader.Number + 1
-		eventsPreviouslySent := make(map[SentEvent]struct{})
+		if subscriber.onStart != nil {
+			if err := subscriber.onStart(subscriptionCtx, id, nil); err != nil {
+				h.log.Warnw("Error starting subscription", "err", err)
+				return
+			}
+		}
 
 		for {
 			select {
 			case <-subscriptionCtx.Done():
 				return
-			case reorg := <-reorgSub.Recv():
-				if err := sendReorg(w, reorg, id); err != nil {
-					h.log.Warnw("Error sending reorg", "err", err)
+			case reorg := <-reorgRecv:
+				if err := subscriber.onReorg(subscriptionCtx, id, reorg); err != nil {
+					h.log.Warnw("Error on reorg", "id", id, "err", err)
+					return
+				}
+			case l1Head := <-l1HeadRecv:
+				if err := subscriber.onL1Head(subscriptionCtx, id, l1Head); err != nil {
+					h.log.Warnw("Error on l1 head", "id", id, "err", err)
+					return
+				}
+			case head := <-newHeadsRecv:
+				if err := subscriber.onNewHead(subscriptionCtx, id, head); err != nil {
+					h.log.Warnw("Error on new head", "id", id, "err", err)
+					return
+				}
+			case pending := <-pendingRecv:
+				if err := subscriber.onPending(subscriptionCtx, id, pending); err != nil {
+					h.log.Warnw("Error on pending", "id", id, "err", err)
 					return
 				}
-				nextBlock = reorg.StartBlockNum
-			case head := <-newHeadsSub.Recv():
-				h.processEvents(subscriptionCtx, w, id, nextBlock, head.Number, fromAddr, keys, eventsPreviouslySent)
-				nextBlock = head.Number + 1
-			case <-pendingSub.Recv():
-				h.processEvents(subscriptionCtx, w, id, nextBlock, nextBlock, fromAddr, keys, eventsPreviouslySent)
 			}
 		}
 	})
 
 	return SubscriptionID(id), nil
 }
 
+// Currently the order of transactions is deterministic, so the transaction always execute on a deterministic state
+// Therefore, the emitted events are deterministic and we can use the transaction hash and event index to identify.
+type SentEvent struct {
+	TransactionHash felt.Felt
+	EventIndex      int
+}
+
+// SubscribeEvents creates a WebSocket stream which will fire events for new Starknet events with applied filters
+func (h *Handler) SubscribeEvents(ctx context.Context, fromAddr *felt.Felt, keys [][]felt.Felt,
+	blockID *SubscriptionBlockID,
+) (SubscriptionID, *jsonrpc.Error) {
+	w, ok := jsonrpc.ConnFromContext(ctx)
+	if !ok {
+		return 0, jsonrpc.Err(jsonrpc.MethodNotFound, nil)
+	}
+
+	lenKeys := len(keys)
+	for _, k := range keys {
+		lenKeys += len(k)
+	}
+	if lenKeys > rpccore.MaxEventFilterKeys {
+		return 0, rpccore.ErrTooManyKeysInFilter
+	}
+
+	requestedHeader, headHeader, rpcErr := h.resolveBlockRange(blockID)
+	if rpcErr != nil {
+		return 0, rpcErr
+	}
+
+	nextBlock := headHeader.Number + 1
+	eventsPreviouslySent := make(map[SentEvent]struct{})
+
+	subscriber := subscriber{
+		onStart: func(ctx context.Context, id uint64, _ any) error {
+			return h.processEvents(ctx, w, id, requestedHeader.Number, headHeader.Number, fromAddr, keys, nil)
+		},
+		onReorg: func(ctx context.Context, id uint64, reorg *sync.ReorgBlockRange) error {
+			if err := sendReorg(w, reorg, id); err != nil {
+				return err
+			}
+			nextBlock = reorg.StartBlockNum
+			return nil
+		},
+		onNewHead: func(ctx context.Context, id uint64, head *core.Block) error {
+			if err := h.processEvents(ctx, w, id, nextBlock, head.Number, fromAddr, keys, eventsPreviouslySent); err != nil {
+				return err
+			}
+			nextBlock = head.Number + 1
+			return nil
+		},
+		onPending: func(ctx context.Context, id uint64, pending *core.Block) error {
+			return h.processEvents(ctx, w, id, nextBlock, nextBlock, fromAddr, keys, eventsPreviouslySent)
+		},
+	}
+	return h.subscribe(ctx, w, subscriber)
+}
+
 // SubscribeTransactionStatus subscribes to status changes of a transaction. It checks for updates each time a new block is added.
 // Later updates are sent only when the transaction status changes.
 // The optional block_id parameter is ignored, as status changes are not stored and historical data cannot be sent.
@@ -318,45 +389,46 @@ func (h *Handler) SubscribeTransactionStatus(ctx context.Context, txHash felt.Fe
 
 func (h *Handler) processEvents(ctx context.Context, w jsonrpc.Conn, id, from, to uint64, fromAddr *felt.Felt,
 	keys [][]felt.Felt, eventsPreviouslySent map[SentEvent]struct{},
-) {
+) error {
 	filter, err := h.bcReader.EventFilter(fromAddr, keys)
 	if err != nil {
 		h.log.Warnw("Error creating event filter", "err", err)
-		return
+		return err
 	}
 
 	defer h.callAndLogErr(filter.Close, "Error closing event filter in events subscription")
 
 	if err = setEventFilterRange(filter, &BlockID{Number: from}, &BlockID{Number: to}, to); err != nil {
 		h.log.Warnw("Error setting event filter range", "err", err)
-		return
+		return err
 	}
 
 	filteredEvents, cToken, err := filter.Events(nil, subscribeEventsChunkSize)
 	if err != nil {
 		h.log.Warnw("Error filtering events", "err", err)
-		return
+		return err
 	}
 
 	err = sendEvents(ctx, w, filteredEvents, eventsPreviouslySent, id)
 	if err != nil {
 		h.log.Warnw("Error sending events", "err", err)
-		return
+		return err
 	}
 
 	for cToken != nil {
 		filteredEvents, cToken, err = filter.Events(cToken, subscribeEventsChunkSize)
 		if err != nil {
 			h.log.Warnw("Error filtering events", "err", err)
-			return
+			return err
 		}
 
 		err = sendEvents(ctx, w, filteredEvents, eventsPreviouslySent, id)
 		if err != nil {
 			h.log.Warnw("Error sending events", "err", err)
-			return
+			return err
 		}
 	}
+	return nil
 }
 
 func sendEvents(ctx context.Context, w jsonrpc.Conn, events []*blockchain.FilteredEvent,
@@ -416,44 +488,18 @@ func (h *Handler) SubscribeNewHeads(ctx context.Context, blockID *SubscriptionBl
 		return 0, rpcErr
 	}
 
-	id := h.idgen()
-	subscriptionCtx, subscriptionCtxCancel := context.WithCancel(ctx)
-	sub := &subscription{
-		cancel: subscriptionCtxCancel,
-		conn:   w,
+	subscriber := subscriber{
+		onStart: func(ctx context.Context, id uint64, _ any) error {
+			return h.sendHistoricalHeaders(ctx, startHeader, latestHeader, w, id)
+		},
+		onReorg: func(ctx context.Context, id uint64, reorg *sync.ReorgBlockRange) error {
+			return sendReorg(w, reorg, id)
+		},
+		onNewHead: func(ctx context.Context, id uint64, head *core.Block) error {
+			return sendHeader(w, head.Header, id)
+		},
 	}
-	h.subscriptions.Store(id, sub)
-
-	newHeadsSub := h.newHeads.Subscribe()
-	reorgSub := h.reorgs.Subscribe() // as per the spec, reorgs are also sent in the new heads subscription
-	sub.wg.Go(func() {
-		defer func() {
-			h.unsubscribe(sub, id)
-			newHeadsSub.Unsubscribe()
-			reorgSub.Unsubscribe()
-		}()
-
-		var wg conc.WaitGroup
-
-		wg.Go(func() {
-			if err := h.sendHistoricalHeaders(subscriptionCtx, startHeader, latestHeader, w, id); err != nil {
-				h.log.Errorw("Error sending old headers", "err", err)
-				return
-			}
-		})
-
-		wg.Go(func() {
-			h.processReorgs(subscriptionCtx, reorgSub, w, id)
-		})
-
-		wg.Go(func() {
-			h.processNewHeaders(subscriptionCtx, newHeadsSub, w, id)
-		})
-
-		wg.Wait()
-	})
-
-	return SubscriptionID(id), nil
+	return h.subscribe(ctx, w, subscriber)
 }
 
 // SubscribePendingTxs creates a WebSocket stream which will fire events when a new pending transaction is added.
@@ -469,74 +515,65 @@ func (h *Handler) SubscribePendingTxs(ctx context.Context, getDetails *bool, sen
 		return 0, rpccore.ErrTooManyAddressesInFilter
 	}
 
-	id := h.idgen()
-	subscriptionCtx, subscriptionCtxCancel := context.WithCancel(ctx)
-	sub := &subscription{
-		cancel: subscriptionCtxCancel,
-		conn:   w,
-	}
-	h.subscriptions.Store(id, sub)
+	sentTxHashes := make(map[felt.Felt]struct{})
+	lastParentHash := felt.Zero
 
-	pendingSub := h.pendingBlock.Subscribe()
-	sub.wg.Go(func() {
-		defer func() {
-			h.unsubscribe(sub, id)
-			pendingSub.Unsubscribe()
-		}()
-
-		h.processPendingTxs(subscriptionCtx, getDetails != nil && *getDetails, senderAddr, pendingSub, w, id)
-	})
-
-	return SubscriptionID(id), nil
-}
-
-func (h *Handler) processPendingTxs(ctx context.Context, getDetails bool, senderAddr []felt.Felt,
-	pendingSub *feed.Subscription[*core.Block], w jsonrpc.Conn, id uint64,
-) {
-	for {
-		select {
-		case <-ctx.Done():
-			return
-		case pendingBlock := <-pendingSub.Recv():
-			filteredTxs := h.filterTxs(pendingBlock.Transactions, getDetails, senderAddr)
-			for _, filteredTxn := range filteredTxs {
-				if err := sendPendingTxs(w, filteredTxn, id); err != nil {
-					h.log.Warnw("Error sending pending transactions", "err", err)
-					return
-				}
+	subscriber := subscriber{
+		onStart: func(ctx context.Context, id uint64, _ any) error {
+			if pending := h.syncReader.PendingBlock(); pending != nil {
+				return h.onPendingBlock(id, w, getDetails, senderAddr, pending, &lastParentHash, sentTxHashes)
 			}
-		}
+			return nil
+		},
+		onPending: func(ctx context.Context, id uint64, pending *core.Block) error {
+			return h.onPendingBlock(id, w, getDetails, senderAddr, pending, &lastParentHash, sentTxHashes)
+		},
 	}
+	return h.subscribe(ctx, w, subscriber)
 }
 
-// filterTxs filters the transactions based on the getDetails flag.
 // If getDetails is true, response will contain the transaction details.
 // If getDetails is false, response will only contain the transaction hashes.
-func (h *Handler) filterTxs(pendingTxs []core.Transaction, getDetails bool, senderAddr []felt.Felt) []any {
-	if getDetails {
-		return h.filterTxDetails(pendingTxs, senderAddr)
+func (h *Handler) onPendingBlock(
+	id uint64,
+	w jsonrpc.Conn,
+	getDetails *bool,
+	senderAddr []felt.Felt,
+	pending *core.Block,
+	lastParentHash *felt.Felt,
+	sentTxHashes map[felt.Felt]struct{},
+) error {
+	if !pending.ParentHash.Equal(lastParentHash) {
+		clear(sentTxHashes)
+		*lastParentHash = *pending.ParentHash
 	}
-	return h.filterTxHashes(pendingTxs, senderAddr)
-}
 
-func (h *Handler) filterTxDetails(pendingTxs []core.Transaction, senderAddr []felt.Felt) []any {
-	filteredTxs := make([]any, 0, len(pendingTxs))
-	for _, txn := range pendingTxs {
-		if h.filterTxBySender(txn, senderAddr) {
-			filteredTxs = append(filteredTxs, AdaptTransaction(txn))
-		}
+	var toResult func(txn core.Transaction) any
+	if getDetails != nil && *getDetails {
+		toResult = toFullTx
+	} else {
+		toResult = toHash
 	}
-	return filteredTxs
-}
 
-func (h *Handler) filterTxHashes(pendingTxs []core.Transaction, senderAddr []felt.Felt) []any {
-	filteredTxHashes := make([]any, 0, len(pendingTxs))
-	for _, txn := range pendingTxs {
-		if h.filterTxBySender(txn, senderAddr) {
-			filteredTxHashes = append(filteredTxHashes, txn.Hash())
+	for _, txn := range pending.Transactions {
+		if _, exist := sentTxHashes[*txn.Hash()]; !exist {
+			if h.filterTxBySender(txn, senderAddr) {
+				if err := sendPendingTxs(w, toResult(txn), id); err != nil {
+					return err
+				}
+			}
+			sentTxHashes[*txn.Hash()] = struct{}{}
 		}
 	}
-	return filteredTxHashes
+	return nil
+}
+
+func toFullTx(txn core.Transaction) any {
+	return AdaptTransaction(txn)
+}
+
+func toHash(txn core.Transaction) any {
+	return txn.Hash()
 }
 
 // filterTxBySender checks if the transaction is included in the sender address list.
@@ -631,20 +668,6 @@ func (h *Handler) sendHistoricalHeaders(
 	}
 }
 
-func (h *Handler) processNewHeaders(ctx context.Context, newHeadsSub *feed.Subscription[*core.Block], w jsonrpc.Conn, id uint64) {
-	for {
-		select {
-		case <-ctx.Done():
-			return
-		case head := <-newHeadsSub.Recv():
-			if err := sendHeader(w, head.Header, id); err != nil {
-				h.log.Warnw("Error sending header", "err", err)
-				return
-			}
-		}
-	}
-}
-
 // sendHeader creates a request and sends it to the client
 func sendHeader(w jsonrpc.Conn, header *core.Header, id uint64) error {
 	return sendResponse("starknet_subscriptionNewHeads", w, id, adaptBlockHeader(header))
```

### rpc/v8/subscriptions_test.go
```diff
@@ -752,6 +752,8 @@ func TestSubscribePendingTxs(t *testing.T) {
 		got := sendWsMessage(t, ctx, conn, subMsg)
 		require.Equal(t, subResp(id), got)
 
+		parentHash := new(felt.Felt).SetUint64(1)
+
 		hash1 := new(felt.Felt).SetUint64(1)
 		addr1 := new(felt.Felt).SetUint64(11)
 
@@ -763,6 +765,9 @@ func TestSubscribePendingTxs(t *testing.T) {
 		hash5 := new(felt.Felt).SetUint64(5)
 
 		syncer.pending.Send(&core.Block{
+			Header: &core.Header{
+				ParentHash: parentHash,
+			},
 			Transactions: []core.Transaction{
 				&core.InvokeTransaction{TransactionHash: hash1, SenderAddress: addr1},
 				&core.DeclareTransaction{TransactionHash: hash2, SenderAddress: addr2},
@@ -790,6 +795,8 @@ func TestSubscribePendingTxs(t *testing.T) {
 		got := sendWsMessage(t, ctx, conn, subMsg)
 		require.Equal(t, subResp(id), got)
 
+		parentHash := new(felt.Felt).SetUint64(1)
+
 		hash1 := new(felt.Felt).SetUint64(1)
 		addr1 := new(felt.Felt).SetUint64(11)
 
@@ -807,6 +814,9 @@ func TestSubscribePendingTxs(t *testing.T) {
 		addr7 := new(felt.Felt).SetUint64(77)
 
 		syncer.pending.Send(&core.Block{
+			Header: &core.Header{
+				ParentHash: parentHash,
+			},
 			Transactions: []core.Transaction{
 				&core.InvokeTransaction{TransactionHash: hash1, SenderAddress: addr1},
 				&core.DeclareTransaction{TransactionHash: hash2, SenderAddress: addr2},
@@ -836,7 +846,11 @@ func TestSubscribePendingTxs(t *testing.T) {
 		got := sendWsMessage(t, ctx, conn, subMsg)
 		require.Equal(t, subResp(id), got)
 
+		parentHash := new(felt.Felt).SetUint64(1)
 		syncer.pending.Send(&core.Block{
+			Header: &core.Header{
+				ParentHash: parentHash,
+			},
 			Transactions: []core.Transaction{
 				&core.InvokeTransaction{
 					TransactionHash:       new(felt.Felt).SetUint64(1),
```
