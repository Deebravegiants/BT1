# [?] Fix a deadlock between the crawler and dialer, and other hangs (#1950)

## Summary
Severity: Unknown
Chain: Zcash
Component: ZcashFoundation/zebra
Published: 2021-04-07
Source: https://github.com/ZcashFoundation/zebra/commit/375c8d8700764534871f02d2d44f847526179dab
Type: security-commit

## Details
Fix a deadlock between the crawler and dialer, and other hangs (#1950)

* Stop ignoring inbound message errors and handshake timeouts

To avoid hangs, Zebra needs to maintain the following invariants in the
handshake and heartbeat code:
- each handshake should run in a separate spawned task
  (not yet implemented)
- every message, error, timeout, and shutdown must update the peer address state
- every await that depends on the network must have a timeout

Once the Connection is created, it should handle timeouts.
But we need to handle timeouts during handshake setup.

* Avoid hangs by adding a timeout to the candidate set update

Also increase the fanout from 1 to 2, to increase address diversity.

But only return permanent errors from `CandidateSet::update`, because
the crawler task exits if `update` returns an error.

Also log Peers response errors in the CandidateSet.

* Use the select macro in the crawler to reduce hangs

The `select` function is biased towards its first argument, risking
starvation.

As a side-benefit, this change also makes the code a lot easier to read
and maintain.

* Split CrawlerAction::Demand into separate actions

This refactor makes the code a bit easier to read, at the cost of
sometimes blocking the crawler on `candidates.next()`.

That's ok, because `next` only has a short (< 100 ms) delay. And we're
just about to spawn a separate task for each handshake.

* Spawn a separate task for each handshake

This change avoids deadlocks by letting each handshake make progress
independently.

* Move the dial task into a separate function

This refactor improves readability.

* Fix buggy future::select function usage

And document the correctness of the new code.

## Patch
### zebra-network/src/constants.rs
```diff
@@ -49,6 +49,14 @@ pub const LIVE_PEER_DURATION: Duration = Duration::from_secs(60 + 20 + 20 + 20);
 /// connected peer.
 pub const HEARTBEAT_INTERVAL: Duration = Duration::from_secs(60);
 
+/// The number of GetAddr requests sent when crawling for new peers.
+///
+/// ## SECURITY
+///
+/// The fanout should be greater than 1, to ensure that Zebra's address book is
+/// not dominated by a single peer.
+pub const GET_ADDR_FANOUT: usize = 2;
+
 /// Truncate timestamps in outbound address messages to this time interval.
 ///
 /// This is intended to prevent a peer from learning exactly when we received
```

### zebra-network/src/peer/connection.rs
```diff
@@ -372,6 +372,22 @@ where
             match self.state {
                 State::AwaitingRequest => {
                     trace!("awaiting client request or peer message");
+                    // CORRECTNESS
+                    //
+                    // Currently, select prefers the first future if multiple
+                    // futures are ready.
+                    //
+                    // The peer can starve client requests if it sends an
+                    // uninterrupted series of messages. But this is unlikely in
+                    // practice, due to network delays.
+                    //
+                    // If both futures are ready, there's no particular reason
+                    // to prefer one over the other.
+                    //
+                    // TODO: use `futures::select!`, which chooses a ready future
+                    //       at random, avoiding starvation
+                    //       (To use `select!`, we'll need to map the different
+                    //       results to a new enum types.)
                     match future::select(peer_rx.next(), self.client_rx.next()).await {
                         Either::Left((None, _)) => {
                             self.fail_with(PeerError::ConnectionClosed);
@@ -404,14 +420,21 @@ where
                         .request_timer
                         .as_mut()
                         .expect("timeout must be set while awaiting response");
-                    let cancel = future::select(timer_ref, tx.cancellation());
-                    match future::select(peer_rx.next(), cancel)
+                    // CORRECTNESS
+                    //
+                    // Currently, select prefers the first future if multiple
+                    // futures are ready.
+                    //
+                    // If multiple futures are ready, we want the cancellation
+                    // to take priority, then the timeout, then peer responses.
+                    let cancel = future::select(tx.cancellation(), timer_ref);
+                    match future::select(cancel, peer_rx.next())
                         .instrument(span.clone())
                         .await
                     {
-                        Either::Left((None, _)) => self.fail_with(PeerError::ConnectionClosed),
-                        Either::Left((Some(Err(e)), _)) => self.fail_with(e),
-                        Either::Left((Some(Ok(peer_msg)), _cancel)) => {
+                        Either::Right((None, _)) => self.fail_with(PeerError::ConnectionClosed),
+                        Either::Right((Some(Err(e)), _)) => self.fail_with(e),
+                        Either::Right((Some(Ok(peer_msg)), _cancel)) => {
                             // Try to process the message using the handler.
                             // This extremely awkward construction avoids
                             // keeping a live reference to handler across the
@@ -455,7 +478,7 @@ where
                                 };
                             }
                         }
-                        Either::Right((Either::Left(_), _peer_fut)) => {
+                        Either::Left((Either::Right(_), _peer_fut)) => {
                             trace!(parent: &span, "client request timed out");
                             let e = PeerError::ClientRequestTimeout;
                             self.state = match self.state {
@@ -478,7 +501,7 @@ where
                                 ),
                             };
                         }
-                        Either::Right((Either::Right(_), _peer_fut)) => {
+                        Either::Left((Either::Left(_), _peer_fut)) => {
                             trace!(parent: &span, "client request was cancelled");
                             self.state = State::AwaitingRequest;
                         }
```

### zebra-network/src/peer/error.rs
```diff
@@ -98,4 +98,13 @@ pub enum HandshakeError {
     /// The remote peer offered a version older than our minimum version.
     #[error("Peer offered obsolete version: {0:?}")]
     ObsoleteVersion(crate::protocol::external::types::Version),
+    /// Sending or receiving a message timed out.
+    #[error("Timeout when sending or receiving a message to peer")]
+    Timeout,
+}
+
+impl From<tokio::time::error::Elapsed> for HandshakeError {
+    fn from(_source: tokio::time::error::Elapsed) -> Self {
+        HandshakeError::Timeout
+    }
 }
```

### zebra-network/src/peer/handshake.rs
```diff
@@ -12,7 +12,7 @@ use futures::{
     channel::{mpsc, oneshot},
     prelude::*,
 };
-use tokio::{net::TcpStream, sync::broadcast};
+use tokio::{net::TcpStream, sync::broadcast, time::timeout};
 use tokio_util::codec::Framed;
 use tower::Service;
 use tracing::{span, Level, Span};
@@ -34,6 +34,12 @@ use super::{Client, Connection, ErrorSlot, HandshakeError, PeerError};
 
 /// A [`Service`] that handshakes with a remote peer and constructs a
 /// client/server pair.
+///
+/// CORRECTNESS
+///
+/// To avoid hangs, each handshake (or its connector) should be:
+/// - launched in a separate task, and
+/// - wrapped in a timeout.
 #[derive(Clone)]
 pub struct Handshake<S> {
     config: Config,
@@ -211,6 +217,10 @@ where
         let fut = async move {
             debug!("connecting to remote peer");
 
+            // CORRECTNESS
+            //
+            // As a defence-in-depth against hangs, every send or next on stream
+            // should be wrapped in a timeout.
             let mut stream = Framed::new(
                 tcp_stream,
                 Codec::builder()
@@ -260,11 +270,10 @@ where
             };
 
             debug!(?version, "sending initial version message");
-            stream.send(version).await?;
+            timeout(constants::REQUEST_TIMEOUT, stream.send(version)).await??;
 
-            let remote_msg = stream
-                .next()
-                .await
+            let remote_msg = timeout(constants::REQUEST_TIMEOUT, stream.next())
+                .await?
                 .ok_or(HandshakeError::ConnectionClosed)??;
 
             // Check that we got a Version and destructure its fields into the local scope.
@@ -293,11 +302,10 @@ where
                 return Err(HandshakeError::NonceReuse);
             }
 
-            stream.send(Message::Verack).await?;
+            timeout(constants::REQUEST_TIMEOUT, stream.send(Message::Verack)).await??;
 
-            let remote_msg = stream
-                .next()
-                .await
+            let remote_msg = timeout(constants::REQUEST_TIMEOUT, stream.next())
+                .await?
                 .ok_or(HandshakeError::ConnectionClosed)??;
             if let Message::Verack = remote_msg {
                 debug!("got verack from remote peer");
@@ -376,22 +384,42 @@ where
                 future::ready(Ok(msg))
             });
 
+            // CORRECTNESS
+            //
+            // Every message and error must update the peer address state via
+            // the inbound_ts_collector.
+            let inbound_ts_collector = timestamp_collector.clone();
             let peer_rx = peer_rx
                 .then(move |msg| {
-                    // Add a metric for inbound messages and fire a timestamp event.
-                    let mut timestamp_collector = timestamp_collector.clone();
+                    // Add a metric for inbound messages and errors.
+                    // Fire a timestamp or failure event.
+                    let mut inbound_ts_collector = inbound_ts_collector.clone();
                     async move {
-                        if let Ok(msg) = &msg {
-                            metrics::counter!(
-                                "zcash.net.in.messages",
-                                1,
-                                "command" => msg.to_string(),
-                                "addr" => addr.to_string(),
-                            );
-                            use futures::sink::SinkExt;
-                            let _ = timestamp_collector
-                                .send(MetaAddr::new_responded(&addr, &remote_services))
-                                .await;
+                        match &msg {
+                            Ok(msg) => {
+                                metrics::counter!(
+                                    "zcash.net.in.messages",
+                                    1,
+                                    "command" => msg.to_string(),
+                                    "addr" => addr.to_string(),
+                                );
+                                // the collector doesn't depend on network activity,
+                                // so this await should not hang
+                                let _ = inbound_ts_collector
+                                    .send(MetaAddr::new_responded(&addr, &remote_services))
+                                    .await;
+                            }
+                            Err(err) => {
+                                metrics::counter!(
+                                    "zebra.net.in.errors",
+                                    1,
+                                    "error" => err.to_string(),
+                                    "addr" => addr.to_string(),
+                                );
+                                let _ = inbound_ts_collector
+                                    .send(MetaAddr::new_errored(&addr, &remote_services))
+                                    .await;
+                            }
                         }
                         msg
                     }
@@ -452,6 +480,16 @@ where
                     .boxed(),
             );
 
+            // CORRECTNESS
+            //
+            // To prevent hangs:
+            // - every await that depends on the network must have a timeout (or interval)
+            // - every error/shutdown must update the address book state and return
+            //
+            // The address book state can be updated via `ClientRequest.tx`, or the
+            // timestamp_collector.
+            //
+            // Returning from the spawned closure terminates the connection's heartbeat task.
             let heartbeat_span = tracing::debug_span!(parent: connection_span, "heartbeat");
             tokio::spawn(
                 async move {
@@ -460,11 +498,23 @@ where
 
                     let mut shutdown_rx = shutdown_rx;
                     let mut server_tx = server_tx;
+                    let mut timestamp_collector = timestamp_collector.clone();
                     let mut interval_stream = tokio::time::interval(constants::HEARTBEAT_INTERVAL);
                     loop {
                         let shutdown_rx_ref = Pin::new(&mut shutdown_rx);
-                        match future::select(interval_stream.next(), shutdown_rx_ref).await {
-                            Either::Left(_) => {
+                        let mut send_addr_err = false;
+
+                        // CORRECTNESS
+                        //
+                        // Currently, select prefers the first future if multiple
+                        // futures are ready.
+                        //
+                        // Starvation is impossible here, because interval has a
+                        // slow rate, and shutdown is a oneshot. If both futures
+                        // are ready, we want the shutdown to take priority over
+                        // sending a useless heartbeat.
+                        match future::select(shutdown_rx_ref, interval_stream.next()).await {
+                            Either::Right(_) => {
                                 let (tx, rx) = oneshot::channel();
                                 let request = Request::Ping(Nonce::default());
                                 tracing::trace!(?request, "queueing heartbeat request");
@@ -474,19 +524,28 @@ where
                                     span: tracing::Span::current(),
                                 }) {
                                     Ok(()) => {
-                                        match server_tx.flush().await {
-                                            Ok(()) => {}
+                                        // TODO: also wait on the shutdown_rx here
+                                        match timeout(
+                                            constants::HEARTBEAT_INTERVAL,
+                                            server_tx.flush(),
+                                        )
+                                        .await
+                                        {
+                                            Ok(Ok(())) => {
+                                            }
+                                            Ok(Err(e)) => {
+                                                tracing::warn!(
+                                                    ?e,
+                                                    "flushing client request failed, shutting down"
+                                                );
+                                                send_addr_err = true;
+                                            }
                                             Err(e) => {
-                                                // We can't get the client request for this failure,
-                                                // so we can't send an error back here. But that's ok,
-                                                // because:
-                                                //   - this error never happens (or it's very rare)
-                                                //   - if the flush() fails, the server hasn't
-                                                //     received the request
                                                 tracing::warn!(
-                                                    "flushing client request failed: {:?}",
-                                                    e
+                                                    ?e,
+                                                    "flushing client request timed out, shutting down"
                                                 );
+                                                send_addr_err = true;
                                             }
                                         }
                                     }
@@ -514,17 +573,46 @@ where
                                 // Heartbeats are checked internally to the
                                 // connection logic, but we need to wait on the
                                 // response to avoid canceling the request.
-                                match rx.await {
-                                    Ok(_) => tracing::trace!("got heartbeat response"),
-                                    Err(_) => {
-                                        tracing::trace!(
+                                //
+                                // TODO: also wait on the shutdown_rx here
+                                match timeout(constants::HEARTBEAT_INTERVAL, rx).await {
+                                    Ok(Ok(_)) => tracing::trace!("got heartbeat response"),
+                                    Ok(Err(e)) => {
+                                        tracing::warn!(
+                                            ?e,
                                             "error awaiting heartbeat response, shutting down"
                                         );
-                                        return;
+                                        send_addr_err = true;
+                                    }
+                                    Err(e) => {
+                                        tracing::warn!(
+                                            ?e,
+                                            "heartbeat response timed out, shutting down"
+                                        );
+                                        send_addr_err = true;
                                     }
                                 }
                             }
-                            Either::Right(_) => return, // got shutdown signal
+                            Either::Left(_) => {
+                                tracing::trace!("shutting down due to Client shut down");
+                                // awaiting a local task won't hang
+                                let _ = timestamp_collector
+                                    .send(MetaAddr::new_shutdown(&addr, &remote_services))
+                                    .await;
+                                return;
+                            }
+                        }
+                        if send_addr_err {
+                            // We can't get the client request for this failure,
+                            // so we can't send an error back on `tx`. So
+                            // we just update the address book with a failure.
+                            let _ = timestamp_collector
+                                .send(MetaAddr::new_errored(
+                                    &addr,
+                                    &remote_services,
+                                ))
+                                .await;
+                            return;
                         }
                     }
                 }
```

### zebra-network/src/peer_set/candidate_set.rs
```diff
@@ -5,10 +5,10 @@ use std::{
 };
 
 use futures::stream::{FuturesUnordered, StreamExt};
-use tokio::time::{sleep, sleep_until, Sleep};
+use tokio::time::{sleep, sleep_until, timeout, Sleep};
 use tower::{Service, ServiceExt};
 
-use crate::{types::MetaAddr, AddressBook, BoxError, Request, Response};
+use crate::{constants, types::MetaAddr, AddressBook, BoxError, Request, Response};
 
 /// The `CandidateSet` manages the `PeerSet`'s peer reconnection attempts.
 ///
@@ -140,6 +140,9 @@ where
     ///
     /// ## Correctness
     ///
+    /// The crawler exits when update returns an error, so it must only return
+    /// errors on permanent failures.
+    ///
     /// The handshaker sets up the peer message receiver so it also sends a
     /// `Responded` peer address update.
     ///
@@ -150,37 +153,62 @@ where
         // Opportunistically crawl the network on every update call to ensure
         // we're actively fetching peers. Continue independently of whether we
         // actually receive any peers, but always ask the network for more.
+        //
         // Because requests are load-balanced across existing peers, we can make
         // multiple requests concurrently, which will be randomly assigned to
         // existing peers, but we don't make too many because update may be
         // called while the peer set is already loaded.
         let mut responses = FuturesUnordered::new();
         trace!("sending GetPeers requests");
-        // Yes this loops only once (for now), until we add fanout back.
-        for _ in 0..1usize {
-            self.peer_service.ready_and().await?;
-            responses.push(self.peer_service.call(Request::Peers));
+        for _ in 0..constants::GET_ADDR_FANOUT {
+            // CORRECTNESS
+            //
+            // avoid deadlocks when there are no connected peers, and:
+            // - we're waiting on a handshake to complete so there are peers, or
+            // - another task that handles or adds peers is waiting on this task to complete.
+            let peer_service =
+                match timeout(constants::REQUEST_TIMEOUT, self.peer_service.ready_and()).await {
+                    // update must only return an error for permanent failures
+                    Err(temporary_error) => {
+                        info!(
+                            ?temporary_error,
+                            "timeout waiting for the peer service to become ready"
+                        );
+                        return Ok(());
+                    }
+                    Ok(Err(permanent_error)) => Err(permanent_error)?,
+                    Ok(Ok(peer_service)) => peer_service,
+                };
+            responses.push(peer_service.call(Request::Peers));
         }
         while let Some(rsp) = responses.next().await {
-            if let Ok(Response::Peers(rsp_addrs)) = rsp {
-                // Filter new addresses to ensure that gossiped addresses are actually new
-                let peer_set = &self.peer_set;
-                let new_addrs = rsp_addrs
-                    .iter()
-                    .filter(|meta| !peer_set.lock().unwrap().contains_addr(&meta.addr))
-                    .collect::<Vec<_>>();
-                trace!(
-                    ?rsp_addrs,
-                    new_addr_count = ?new_addrs.len(),
-                    "got response to GetPeers"
-                );
-                // New addresses are deserialized in the `NeverAttempted` state
-                peer_set
-                    .lock()
-                    .unwrap()
-                    .extend(new_addrs.into_iter().cloned());
-            } else {
-                trace!("got error in GetPeers request");
+            match rsp {
+                Ok(Response::Peers(rsp_addrs)) => {
+                    // Filter new addresses to ensure that gossiped addresses are actually new
+                    let peer_set = &self.peer_set;
+                    // TODO: reduce mutex contention by moving the filtering into
+                    // the address book itself
+                    let new_addrs = rsp_addrs
+                        .iter()
+                        .filter(|meta| !peer_set.lock().unwrap().contains_addr(&meta.addr))
+                        .collect::<Vec<_>>();
+                    trace!(
+                        ?rsp_addrs,
+                        new_addr_count = ?new_addrs.len(),
+                        "got response to GetPeers"
+                    );
+                    // New addresses are deserialized in the `NeverAttempted` state
+                    peer_set
+                        .lock()
+                        .unwrap()
+                        .extend(new_addrs.into_iter().cloned());
+                }
+                Err(e) => {
+                    // since we do a fanout, and new updates are triggered by
+                    // each demand, we can ignore errors in individual responses
+                    trace!(?e, "got error in GetPeers request");
+                }
+                Ok(_) => unreachable!("Peers requests always return Peers responses"),
             }
         }
 
@@ -214,6 +242,16 @@ where
         let mut sleep = sleep_until(current_deadline + Self::MIN_PEER_CONNECTION_INTERVAL);
         mem::swap(&mut self.next_peer_min_wait, &mut sleep);
 
+        // CORRECTNESS
+        //
+        // In this critical section, we hold the address mutex.
+        //
+        // To avoid deadlocks, the critical section:
+        // - must not acquire any other locks
+        // - must not await any futures
+        //
+        // To avoid hangs, any computation in the critical section should
+        // be kept to a minimum.
         let reconnect = {
             let mut peer_set_guard = self.peer_set.lock().unwrap();
             // It's okay to early return here because we're returning None
```

### zebra-network/src/peer_set/initialize.rs
```diff
@@ -17,6 +17,7 @@ use futures::{
 use tokio::{
     net::{TcpListener, TcpStream},
     sync::broadcast,
+    time::Instant,
 };
 use tower::{
     buffer::Buffer, discover::Change, layer::Layer, load::peak_ewma::PeakEwmaDiscover,
@@ -26,14 +27,15 @@ use tracing::Span;
 use tracing_futures::Instrument;
 
 use crate::{
-    constants, peer, timestamp_collector::TimestampCollector, AddressBook, BoxError, Config,
-    Request, Response,
+    constants, meta_addr::MetaAddr, peer, timestamp_collector::TimestampCollector, AddressBook,
+    BoxError, Config, Request, Response,
 };
 
 use zebra_chain::parameters::Network;
 
 use super::CandidateSet;
 use super::PeerSet;
+use peer::Client;
 
 type PeerChange = Result<Change<SocketAddr, peer::Client>, BoxError>;
 
@@ -267,45 +269,78 @@ where
     }
 }
 
-/// Given a channel that signals a need for new peers, try to connect to a peer
-/// and send the resulting `peer::Client` through a channel.
-#[instrument(skip(
-    crawl_new_peer_interval,
-    demand_tx,
-    demand_rx,
-    candidates,
-    connector,
-    success_tx
-))]
+/// An action that the peer crawler can take.
+#[allow(dead_code)]
+enum CrawlerAction {
+    /// Drop the demand signal because there are too many pending handshakes.
+    DemandDrop,
+    /// Initiate a handshake to `candidate` in response to demand.
+    DemandHandshake { candidate: MetaAddr },
+    /// Crawl existing peers for more peers in response to demand, because there
+    /// are no available candidates.
+    DemandCrawl,
+    /// Crawl existing peers for more peers in response to a timer `tick`.
+    TimerCrawl { tick: Instant },
+    /// Handle a successfully connected handshake `peer_set_change`.
+    HandshakeConnected {
+        peer_set_change: Change<SocketAddr, Client>,
+    },
+    /// Handle a handshake failure to `failed_addr`.
+    HandshakeFailed { failed_addr: MetaAddr },
+}
+
+/// Given a channel `demand_rx` that signals a need for new peers, try to find
+/// and connect to new peers, and send the resulting `peer::Client`s through the
+/// `success_tx` channel.
+///
+/// Crawl for new peers every `crawl_new_peer_interval`, and whenever there is
+/// demand, but no new peers in `candidates`. After crawling, try to connect to
+/// one new peer using `connector`.
+///
+/// If a handshake fails, restore the unused demand signal by sending it to
+/// `demand_tx`.
+///
+/// The crawler terminates when `candidates.update()` or `success_tx` returns a
+/// permanent internal error. Transient errors and individual peer errors should
+/// be handled within the crawler.
+#[instrument(skip(demand_tx, demand_rx, candidates, connector, success_tx))]
 async fn crawl_and_dial<C, S>(
     crawl_new_peer_interval: std::time::Duration,
     mut demand_tx: mpsc::Sender<()>,
     mut demand_rx: mpsc::Receiver<()>,
     mut candidates: CandidateSet<S>,
-    mut connector: C,
+    connector: C,
     mut success_tx: mpsc::Sender<PeerChange>,
 ) -> Result<(), BoxError>
 where
-    C: Service<SocketAddr, Response = Change<SocketAddr, peer::Client>, Error = BoxError> + Clone,
+    C: Service<SocketAddr, Response = Change<SocketAddr, peer::Client>, Error = BoxError>
+        + Clone
+        + Send
+        + 'static,
     C::Future: Send + 'static,
     S: Service<Request, Response = Response, Error = BoxError>,
     S::Future: Send + 'static,
 {
-    use futures::{
-        future::{
-            select,
-            Either::{Left, Right},
-        },
-        TryFutureExt,
-    };
+    use CrawlerAction::*;
+
+    // CORRECTNESS
+    //
+    // To avoid hangs and starvation, the crawler must:
+    // - spawn a separate task for each crawl and handshake, so they can make
+    //   progress independently (and avoid deadlocking each other)
+    // - use the `select!` macro for all actions, because the `select` function
+    //   is biased towards the first ready future
 
     let mut handshakes = FuturesUnordered::new();
     // <FuturesUnordered as Stream> returns None when empty.
     // Keeping an unresolved future in the pool means the stream
     // never terminates.
+    // We could use StreamExt::select_next_some and StreamExt::fuse, but `fuse`
+    // prevents us from adding items to the stream and checking its length.
     handshakes.push(future::pending().boxed());
 
-    let mut crawl_timer = tokio::time::interval(crawl_new_peer_interval);
+    let mut crawl_timer =
+        tokio::time::interval(crawl_new_peer_interval).map(|tick| TimerCrawl { tick });
 
     loop {
         metrics::gauge!(
@@ -315,74 +350,125 @@ where
                 .checked_sub(1)
                 .expect("the pool always contains an unresolved future") as f64
         );
-        // This is a little awkward because there's no select3.
-        match select(
-            select(demand_rx.next(), crawl_timer.next()),
-            handshakes.next(),
-        )
-        .await
-        {
-            Left((Left((Some(_demand), _)), _)) => {
+
+        let crawler_action = tokio::select! {
+            a = handshakes.next() => a.expect("handshakes never terminates, because it contains a future that never resolves"),
+            a = crawl_timer.next() => a.expect("timers never terminate"),
+            // turn the demand into an action, based on the crawler's current state
+            _ = demand_rx.next() => {
                 if handshakes.len() > 50 {
-                    // This is set to trace level because when the peerset is
-                    // congested it can generate a lot of demand signal very rapidly.
-                    trace!("too many in-flight handshakes, dropping demand signal");
-                    continue;
-                }
-                if let Some(candidate) = candidates.next().await {
-                    debug!(?candidate.addr, "attempting outbound connection in response to demand");
-                    connector.ready_and().await?;
-                    handshakes.push(
-                        connector
-                            .call(candidate.addr)
-                            .map_err(move |e| {
-                                debug!(?candidate.addr, ?e, "failed to connect to candidate");
-                                candidate
-                            })
-                            .boxed(),
-                    );
+                    // Too many pending handshakes already
+                    DemandDrop
+                } else if let Some(candidate) = candidates.next().await {
+                    // candidates.next has a short delay, and briefly holds the address
+                    // book lock, so it shouldn't hang
+                    DemandHandshake { candidate }
                 } else {
-                    debug!("demand for peers but no available candidates");
-                    candidates.update().await?;
-                    // Try to connect to a new peer.
-                    let _ = demand_tx.try_send(());
+                    DemandCrawl
                 }
             }
-            // did a drill sergeant write this? no there's just no Either3
-            Left((Right((Some(_timer), _)), _)) => {
-                debug!("crawling for more peers");
+        };
+
+        match crawler_action {
+            DemandDrop => {
+                // This is set to trace level because when the peerset is
+                // congested it can generate a lot of demand signal very
+                // rapidly.
+                trace!("too many in-flight handshakes, dropping demand signal");
+                continue;
+            }
+            DemandHandshake { candidate } => {
+                // spawn each handshake into an independent task, so it can make
+                // progress independently of the crawls
+                let hs_join =
+                    tokio::spawn(dial(candidate, connector.clone())).map(move |res| match res {
+                        Ok(crawler_action) => crawler_action,
+                        Err(e) => {
+                            panic!("panic during handshaking with {:?}: {:?} ", candidate, e);
+                        }
+                    });
+                handshakes.push(Box::pin(hs_join));
+            }
+            DemandCrawl => {
+                debug!("demand for peers but no available candidates");
+                // update has timeouts, and briefly holds the address book
+                // lock, so it shouldn't hang
+                //
+                // TODO: refactor candidates into a buffered service, so we can
+                //       spawn independent tasks to avoid deadlocks
+                candidates.update().await?;
+                // Try to connect to a new peer.
+                let _ = demand_tx.try_send(());
+            }
+            TimerCrawl { tick } => {
+                debug!(
+                    ?tick,
+                    "crawling for more peers in response to the crawl timer"
+                );
+                // TODO: spawn independent tasks to avoid deadlocks
                 candidates.update().await?;
                 // Try to connect to a new peer.
                 let _ = demand_tx.try_send(());
             }
-            Right((Some(Ok(change)), _)) => {
-                if let Change::Insert(ref addr, _) = change {
+            HandshakeConnected { peer_set_change } => {
+                if let Change::Insert(ref addr, _) = peer_set_change {
                     debug!(candidate.addr = ?addr, "successfully dialed new peer");
                 } else {
                     unreachable!("unexpected handshake result: all changes should be Insert");
                 }
-                success_tx.send(Ok(change)).await?;
+                // successes are handled by an independent task, so they
+                // shouldn't hang
+                success_tx.send(Ok(peer_set_change)).await?;
             }
-            Right((Some(Err(candidate)), _)) => {
-                debug!(?candidate.addr, "marking candidate as failed");
-                candidates.report_failed(&candidate);
+            HandshakeFailed { failed_addr } => {
+                debug!(?failed_addr.addr, "marking candidate as failed");
+                candidates.report_failed(&failed_addr);
                 // The demand signal that was taken out of the queue
                 // to attempt to connect to the failed candidate never
                 // turned into a connection, so add it back:
                 let _ = demand_tx.try_send(());
             }
-            // We don't expect to see these patterns during normal operation
-            Left((Left((None, _)), _)) => {
-                unreachable!("demand_rx never fails, because we hold demand_tx");
-            }
-            Left((Right((None, _)), _)) => {
-                unreachable!("crawl_timer never terminates");
-            }
-            Right((None, _)) => {
-                unreachable!(
-                    "handshakes never terminates, because it contains a future that never resolves"
-                );
-            }
         }
     }
 }
+
+/// Try to connect to `candidate` using `connector`.
+///
+/// Returns a `HandshakeConnected` action on success, and a
+/// `HandshakeFailed` action on error.
+#[instrument(skip(connector,))]
+async fn dial<C>(candidate: MetaAddr, mut connector: C) -> CrawlerAction
+where
+    C: Service<SocketAddr, Response = Change<SocketAddr, peer::Client>, Error = BoxError>
+        + Clone
+        + Send
+        + 'static,
+    C::Future: Send + 'static,
+{
+    use CrawlerAction::*;
+
+    // CORRECTNESS
+    //
+    // To avoid hangs, the dialer must only await:
+    // - functions that return immediately, or
+    // - functions that have a reasonable timeout
+
+    debug!(?candidate.addr, "attempting outbound connection in response to demand");
+
+    // the connector is always ready, so this can't hang
+    let connector = connector.ready_and().await.expect("connector never errors");
+
+    // the handshake has timeouts, so it shouldn't hang
+    connector
+        .call(candidate.addr)
+        .map(move |res| match res {
+            Ok(peer_set_change) => HandshakeConnected { peer_set_change },
+            Err(e) => {
+                debug!(?candidate.addr, ?e, "failed to connect to candidate");
+                HandshakeFailed {
+                    failed_addr: candidate,
+                }
+            }
+        })
+        .await
+}
```
