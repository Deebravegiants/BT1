# [?] sc-transaction-handler: Fix potential crashes on exit (#12807)

## Summary
Severity: Unknown
Chain: Polkadot
Component: paritytech/substrate
Published: 2022-11-30
Source: https://github.com/paritytech/substrate/commit/cc369313ae0ffac089dacd3a7334b785d59dd9ed
Type: security-commit

## Details
sc-transaction-handler: Fix potential crashes on exit (#12807)

This fixes some potential crashes in the stream handling in `sc-transaction-handler`.

## Patch
### client/network/transactions/src/lib.rs
```diff
@@ -172,11 +172,13 @@ impl TransactionsHandlerPrototype {
 
 		let handler = TransactionsHandler {
 			protocol_name: self.protocol_name,
-			propagate_timeout: Box::pin(interval(PROPAGATE_TIMEOUT)),
+			propagate_timeout: (Box::pin(interval(PROPAGATE_TIMEOUT))
+				as Pin<Box<dyn Stream<Item = ()> + Send>>)
+				.fuse(),
 			pending_transactions: FuturesUnordered::new(),
 			pending_transactions_peers: HashMap::new(),
 			service,
-			event_stream,
+			event_stream: event_stream.fuse(),
 			peers: HashMap::new(),
 			transaction_pool,
 			from_controller,
@@ -229,7 +231,7 @@ pub struct TransactionsHandler<
 > {
 	protocol_name: ProtocolName,
 	/// Interval at which we call `propagate_transactions`.
-	propagate_timeout: Pin<Box<dyn Stream<Item = ()> + Send>>,
+	propagate_timeout: stream::Fuse<Pin<Box<dyn Stream<Item = ()> + Send>>>,
 	/// Pending transactions verification tasks.
 	pending_transactions: FuturesUnordered<PendingTransaction<H>>,
 	/// As multiple peers can send us the same transaction, we group
@@ -240,7 +242,7 @@ pub struct TransactionsHandler<
 	/// Network service to use to send messages and manage peers.
 	service: S,
 	/// Stream of networking events.
-	event_stream: Pin<Box<dyn Stream<Item = Event> + Send>>,
+	event_stream: stream::Fuse<Pin<Box<dyn Stream<Item = Event> + Send>>>,
 	// All connected peers
 	peers: HashMap<PeerId, Peer<H>>,
 	transaction_pool: Arc<dyn TransactionPool<H, B>>,
@@ -268,7 +270,7 @@ where
 	pub async fn run(mut self) {
 		loop {
 			futures::select! {
-				_ = self.propagate_timeout.next().fuse() => {
+				_ = self.propagate_timeout.next() => {
 					self.propagate_transactions();
 				},
 				(tx_hash, result) = self.pending_transactions.select_next_some() => {
@@ -278,15 +280,15 @@ where
 						warn!(target: "sub-libp2p", "Inconsistent state, no peers for pending transaction!");
 					}
 				},
-				network_event = self.event_stream.next().fuse() => {
+				network_event = self.event_stream.next() => {
 					if let Some(network_event) = network_event {
 						self.handle_network_event(network_event).await;
 					} else {
 						// Networking has seemingly closed. Closing as well.
 						return;
 					}
 				},
-				message = self.from_controller.select_next_some().fuse() => {
+				message = self.from_controller.select_next_some() => {
 					match message {
 						ToHandler::PropagateTransaction(hash) => self.propagate_transaction(&hash),
 						ToHandler::PropagateTransactions => self.propagate_transactions(),
```
