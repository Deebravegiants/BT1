# [?] Add reentrancy guard for `process_pending_htlc_forwards`

## Summary
Severity: Unknown
Chain: Bitcoin/Lightning
Component: lightningdevkit/rust-lightning
Published: 2025-07-03
Source: https://github.com/lightningdevkit/rust-lightning/commit/6985f5368375319ab4413db576cdaf3c300e7618
Type: security-commit

## Details
Add reentrancy guard for `process_pending_htlc_forwards`

We add a reentrancy guard to disallow entering
`process_pending_htlc_forwards` multiple times. This makes sure that
we'd skip any additional processing calls if a prior round/batch of
processing is still underway.

## Patch
### lightning/src/ln/channelmanager.rs
```diff
@@ -2720,6 +2720,10 @@ pub struct ChannelManager<
 	/// A simple atomic flag to ensure only one task at a time can be processing events asynchronously.
 	pending_events_processor: AtomicBool,
 
+	/// A simple atomic flag to ensure only one task at a time can be processing HTLC forwards via
+	/// [`Self::process_pending_htlc_forwards`].
+	pending_htlc_forwards_processor: AtomicBool,
+
 	/// If we are running during init (either directly during the deserialization method or in
 	/// block connection methods which run after deserialization but before normal operation) we
 	/// cannot provide the user with [`ChannelMonitorUpdate`]s through the normal update flow -
@@ -3796,6 +3800,7 @@ where
 
 			pending_events: Mutex::new(VecDeque::new()),
 			pending_events_processor: AtomicBool::new(false),
+			pending_htlc_forwards_processor: AtomicBool::new(false),
 			pending_background_events: Mutex::new(Vec::new()),
 			total_consistency_lock: RwLock::new(()),
 			background_events_processed_since_startup: AtomicBool::new(false),
@@ -6338,9 +6343,19 @@ where
 	/// Users implementing their own background processing logic should call this in irregular,
 	/// randomly-distributed intervals.
 	pub fn process_pending_htlc_forwards(&self) {
+		if self
+			.pending_htlc_forwards_processor
+			.compare_exchange(false, true, Ordering::Acquire, Ordering::Relaxed)
+			.is_err()
+		{
+			return;
+		}
+
 		let _persistence_guard = PersistenceNotifierGuard::optionally_notify(self, || {
 			self.internal_process_pending_htlc_forwards()
 		});
+
+		self.pending_htlc_forwards_processor.store(false, Ordering::Release);
 	}
 
 	// Returns whether or not we need to re-persist.
@@ -16474,6 +16489,7 @@ where
 
 			pending_events: Mutex::new(pending_events_read),
 			pending_events_processor: AtomicBool::new(false),
+			pending_htlc_forwards_processor: AtomicBool::new(false),
 			pending_background_events: Mutex::new(pending_background_events),
 			total_consistency_lock: RwLock::new(()),
 			background_events_processed_since_startup: AtomicBool::new(false),
```
