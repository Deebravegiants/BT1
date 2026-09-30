# [?] Avoid panic on dropping a `sc_network::service::out_events::Receiver`. (#6458)

## Summary
Severity: Unknown
Chain: Polkadot
Component: paritytech/substrate
Published: 2020-06-23
Source: https://github.com/paritytech/substrate/commit/19826b979b1874883837a7b3e30470f655a2a8e6
Type: security-commit

## Details
Avoid panic on dropping a `sc_network::service::out_events::Receiver`. (#6458)

* Avoid panic on dropping a `Receiver`.

* CI

## Patch
### client/network/src/service/out_events.rs
```diff
@@ -35,7 +35,7 @@
 use crate::Event;
 use super::maybe_utf8_bytes_to_string;
 
-use futures::{prelude::*, channel::mpsc, ready};
+use futures::{prelude::*, channel::mpsc, ready, stream::FusedStream};
 use parking_lot::Mutex;
 use prometheus_endpoint::{register, CounterVec, GaugeVec, Opts, PrometheusError, Registry, U64};
 use std::{
@@ -119,8 +119,10 @@ impl fmt::Debug for Receiver {
 
 impl Drop for Receiver {
 	fn drop(&mut self) {
-		// Empty the list to properly decrease the metrics.
-		while let Some(Some(_)) = self.next().now_or_never() {}
+		if !self.inner.is_terminated() {
+			// Empty the list to properly decrease the metrics.
+			while let Some(Some(_)) = self.next().now_or_never() {}
+		}
 	}
 }
 
```
