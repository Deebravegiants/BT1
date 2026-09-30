# [?] fix: PRO-1330 - Move Location::panic() to inside the function, so it outputs the caller of the fn and not of the async block poll fn. (#4769)

## Summary
Severity: Unknown
Chain: Chainflip
Component: chainflip-io/chainflip-backend
Published: 2024-04-17
Source: https://github.com/chainflip-io/chainflip-backend/commit/307b3632b253a3275636de40745d5c49de9a783d
Type: security-commit

## Details
fix: PRO-1330 - Move Location::panic() to inside the function, so it outputs the caller of the fn and not of the async block poll fn. (#4769)

## Patch
### utilities/src/with_std/spmc.rs
```diff
@@ -21,13 +21,14 @@ impl<T: Clone> Sender<T> {
 	#[allow(clippy::manual_async_fn)]
 	#[track_caller]
 	pub fn send(&self, msg: T) -> impl futures::Future<Output = bool> + '_ {
+		let caller_location = core::panic::Location::caller();
 		async move {
 			match self.sender.try_broadcast(msg) {
 				Ok(None) => true,
 				Ok(Some(_)) => unreachable!("async_broadcast feature unused"),
 				Err(error) => match error {
 					async_broadcast::TrySendError::Full(msg) => {
-						warn!("Waiting for space in channel which is currently full with a capacity of {} items at {}", self.sender.capacity(), core::panic::Location::caller());
+						warn!("Waiting for space in channel which is currently full with a capacity of {} items at {}", self.sender.capacity(), caller_location);
 						match self.sender.broadcast(msg).await {
 							Ok(None) => true,
 							Ok(Some(_)) => unreachable!("async_broadcast feature unused"),
```
