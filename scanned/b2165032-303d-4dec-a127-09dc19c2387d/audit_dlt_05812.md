# [?] Fix WASM block producer panic (#11206)

## Summary
Severity: Unknown
Chain: Polkadot
Component: paritytech/substrate
Published: 2022-04-13
Source: https://github.com/paritytech/substrate/commit/32510e13afa84a2fa917a94e5d7e18d480a34a22
Type: security-commit

## Details
Fix WASM block producer panic (#11206)

* Box events

Signed-off-by: Oliver Tale-Yazdi <oliver.tale-yazdi@parity.io>

* Fix tests

Signed-off-by: Oliver Tale-Yazdi <oliver.tale-yazdi@parity.io>

* Revert "Box events"

This reverts commit 9fb1887cd23eb272844d63640b0b2d9ba3e549a1.

* Revert "Fix tests"

This reverts commit 981c50f23a7c514c9527299734bc6bc5b77a817f.

* Use simpler approach

Signed-off-by: Oliver Tale-Yazdi <oliver.tale-yazdi@parity.io>

* Update doc

Signed-off-by: Oliver Tale-Yazdi <oliver.tale-yazdi@parity.io>

## Patch
### frame/system/src/lib.rs
```diff
@@ -591,11 +591,14 @@ pub mod pallet {
 
 	/// Events deposited for the current block.
 	///
-	/// NOTE: This storage item is explicitly unbounded since it is never intended to be read
-	/// from within the runtime.
+	/// NOTE: The item is unbound and should therefore never be read on chain.
+	/// It could otherwise inflate the PoV size of a block.
+	///
+	/// Events have a large in-memory size. Box the events to not go out-of-memory
+	/// just in case someone still reads them from within the runtime.
 	#[pallet::storage]
 	pub(super) type Events<T: Config> =
-		StorageValue<_, Vec<EventRecord<T::Event, T::Hash>>, ValueQuery>;
+		StorageValue<_, Vec<Box<EventRecord<T::Event, T::Hash>>>, ValueQuery>;
 
 	/// The number of events in the `Events<T>` list.
 	#[pallet::storage]
@@ -1213,7 +1216,7 @@ impl<T: Config> Pallet<T> {
 			old_event_count
 		};
 
-		Events::<T>::append(&event);
+		Events::<T>::append(event);
 
 		for topic in topics {
 			<EventTopics<T>>::append(topic, &(block_number, event_idx));
@@ -1380,14 +1383,16 @@ impl<T: Config> Pallet<T> {
 	/// items for any behavior like this.
 	#[cfg(any(feature = "std", feature = "runtime-benchmarks", test))]
 	pub fn events() -> Vec<EventRecord<T::Event, T::Hash>> {
-		Self::read_events_no_consensus()
+		// Dereferencing the events here is fine since we are not in the
+		// memory-restricted runtime.
+		Self::read_events_no_consensus().into_iter().map(|e| *e).collect()
 	}
 
 	/// Get the current events deposited by the runtime.
 	///
 	/// Should only be called if you know what you are doing and outside of the runtime block
 	/// execution else it can have a large impact on the PoV size of a block.
-	pub fn read_events_no_consensus() -> Vec<EventRecord<T::Event, T::Hash>> {
+	pub fn read_events_no_consensus() -> Vec<Box<EventRecord<T::Event, T::Hash>>> {
 		Events::<T>::get()
 	}
 
```
