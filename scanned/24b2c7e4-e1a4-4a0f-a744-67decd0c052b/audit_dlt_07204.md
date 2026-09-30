# [?] network: avoid panic when shutting down cleanly.

## Summary
Severity: Unknown
Chain: Zcash
Component: ZcashFoundation/zebra
Published: 2020-07-22
Source: https://github.com/ZcashFoundation/zebra/commit/4a41c9254ddcfae218a77d382cdc3fb336d3acec
Type: security-commit

## Details
network: avoid panic when shutting down cleanly.

When the connection sees the client_rx channel close it knows it will never get
any more requests, and it should terminate.  But instead of terminating, it
errored itself, and the method to error itself tries to pull all the
outstanding client requests from the channel in order to fail them before it
shuts down.  This results in reading from a closed channel, causing a panic.
Instead we return cleanly rather than failing (since we know there are no
outstanding requests, as the channel is closed).

## Patch
### zebra-network/src/peer/connection.rs
```diff
@@ -190,7 +190,8 @@ where
                             self.handle_message_as_request(msg).await
                         }
                         Either::Right((None, _)) => {
-                            self.fail_with(PeerError::DeadClient);
+                            trace!("client_rx closed, ending connection");
+                            return;
                         }
                         Either::Right((Some(req), _)) => {
                             let span = req.span.clone();
```

### zebra-network/src/peer/error.rs
```diff
@@ -26,10 +26,6 @@ pub enum PeerError {
     /// The remote peer closed the connection.
     #[error("Peer closed connection")]
     ConnectionClosed,
-    /// The [`peer::Client`] half of the [`peer::Client`]/[`peer::Server`] pair died before
-    /// the [`Server`] half did.
-    #[error("peer::Client instance died")]
-    DeadClient,
     /// The remote peer did not respond to a [`peer::Client`] request in time.
     #[error("Client request timed out")]
     ClientRequestTimeout,
```
